[CmdletBinding()]
param(
    [string[]]$Priorities = @('P0','P1','P2'),
    [string]$RequestCsv = '',
    [string]$OutputRoot = ''
)

# Resolve paths only after param() has finished. This works reliably in Windows PowerShell 5.1.
# The CMD launchers cd into the tool directory first, so the execution directory is the tool folder.
$BaseDir = (Get-Location).Path
if ([string]::IsNullOrWhiteSpace($RequestCsv)) {
    $RequestCsv = Join-Path $BaseDir 'SOURCE_BACKFILL_REQUEST_V96.csv'
}
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $BaseDir 'results'
}

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Windows PowerShell 5.1 treats UTF-8 files without BOM as ANSI.
# Keep this script ASCII-only and explicitly read the request CSV as UTF-8.
# Also accept comma-delimited priority input from powershell.exe -File.
$Priorities = @(
    $Priorities | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }
)

function Get-SafeName([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return 'source' }
    $s = $Value -replace '[^\p{L}\p{Nd}]+', '_'
    $s = $s.Trim('_')
    if ($s.Length -gt 70) { $s = $s.Substring(0,70).Trim('_') }
    if ([string]::IsNullOrWhiteSpace($s)) { return 'source' }
    return $s
}

function Test-Magic([string]$Path, [string]$Extension) {
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $fi = Get-Item -LiteralPath $Path
    if ($fi.Length -lt 4) { return $false }
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $buf = New-Object byte[] 8
        $n = $stream.Read($buf,0,$buf.Length)
    } finally {
        $stream.Dispose()
    }
    $ext = $Extension.ToLowerInvariant()
    if ($ext -eq '.pdf') {
        return ($n -ge 4 -and $buf[0] -eq 0x25 -and $buf[1] -eq 0x50 -and $buf[2] -eq 0x44 -and $buf[3] -eq 0x46)
    }
    if ($ext -eq '.zip' -or $ext -eq '.xlsx') {
        return ($n -ge 2 -and $buf[0] -eq 0x50 -and $buf[1] -eq 0x4B)
    }
    if ($ext -eq '.xls') {
        # Legacy OLE/CFBF signature D0 CF 11 E0 A1 B1 1A E1
        return ($n -ge 8 -and $buf[0] -eq 0xD0 -and $buf[1] -eq 0xCF -and $buf[2] -eq 0x11 -and $buf[3] -eq 0xE0 -and $buf[4] -eq 0xA1 -and $buf[5] -eq 0xB1 -and $buf[6] -eq 0x1A -and $buf[7] -eq 0xE1)
    }
    return $true
}

function Invoke-CurlAttempt([object]$CurlCommand, [string]$Url, [string]$Destination, [bool]$Insecure) {
    $stderr = "$Destination.curl.stderr.txt"
    Remove-Item -LiteralPath $stderr -Force -ErrorAction SilentlyContinue

    $args = @(
        '--location','--fail','--silent','--show-error','--ssl-no-revoke',
        '--retry','4','--retry-delay','2','--connect-timeout','30','--max-time','900',
        '--user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 SourceBackfill/1.0'
    )
    if ($Insecure) {
        $args += '--insecure'
    }
    $args += @(
        '--output',$Destination,
        '--write-out','%{http_code}|%{content_type}|%{url_effective}',
        '--',$Url
    )

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $meta = & $CurlCommand.Source @args 2> $stderr
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    $errText = ''
    if (Test-Path -LiteralPath $stderr) {
        $rawErr = Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue
        if ($null -ne $rawErr) {
            $errText = ([string]$rawErr).Trim()
        }
        Remove-Item -LiteralPath $stderr -Force -ErrorAction SilentlyContinue
    }

    $parts = @('','','')
    if ($null -ne $meta -and -not [string]::IsNullOrWhiteSpace([string]$meta)) {
        $tmp = ([string]$meta).Split('|',3)
        for ($i=0; $i -lt $tmp.Length; $i++) { $parts[$i] = $tmp[$i] }
    }

    return [pscustomobject]@{
        ExitCode = $exitCode
        HttpStatus = $parts[0]
        ContentType = $parts[1]
        EffectiveUrl = $parts[2]
        Error = $errText
        Insecure = $Insecure
    }
}

function Download-WithCurl([string]$Url, [string]$Destination) {
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if (-not $curl) { return $null }

    $first = Invoke-CurlAttempt $curl $Url $Destination $false
    if ($first.ExitCode -eq 0) {
        return [pscustomobject]@{
            Ok = $true
            HttpStatus = $first.HttpStatus
            ContentType = $first.ContentType
            EffectiveUrl = $first.EffectiveUrl
            Error = ''
            Warning = ''
            Method = 'curl.exe'
            TlsValidation = 'SCHANNEL_DEFAULT_SSL_NO_REVOKE'
        }
    }

    $wrongPrincipal = ($first.ExitCode -eq 60) -and (
        $first.Error -match 'SEC_E_WRONG_PRINCIPAL' -or
        $first.Error -match 'SNI or certificate check failed' -or
        $first.Error -match 'target principal name is incorrect'
    )

    if ($wrongPrincipal) {
        Write-Host '  TLS hostname mismatch: reintentando solo esta fuente con curl --insecure.' -ForegroundColor DarkYellow
        Remove-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        $second = Invoke-CurlAttempt $curl $Url $Destination $true
        if ($second.ExitCode -eq 0) {
            return [pscustomobject]@{
                Ok = $true
                HttpStatus = $second.HttpStatus
                ContentType = $second.ContentType
                EffectiveUrl = $second.EffectiveUrl
                Error = ''
                Warning = 'TLS hostname verification bypassed after SEC_E_WRONG_PRINCIPAL. Binary still requires magic-byte and SHA-256 validation.'
                Method = 'curl.exe --insecure'
                TlsValidation = 'BYPASSED_WRONG_PRINCIPAL'
            }
        }
        return [pscustomobject]@{
            Ok = $false
            HttpStatus = $second.HttpStatus
            ContentType = $second.ContentType
            EffectiveUrl = $second.EffectiveUrl
            Error = ('verified curl: {0} | insecure retry: {1}' -f $first.Error,$second.Error)
            Warning = 'TLS hostname verification bypass was attempted but download still failed.'
            Method = 'curl.exe + curl.exe --insecure'
            TlsValidation = 'BYPASS_ATTEMPT_FAILED'
        }
    }

    return [pscustomobject]@{
        Ok = $false
        HttpStatus = $first.HttpStatus
        ContentType = $first.ContentType
        EffectiveUrl = $first.EffectiveUrl
        Error = $first.Error
        Warning = ''
        Method = 'curl.exe'
        TlsValidation = 'SCHANNEL_DEFAULT_SSL_NO_REVOKE'
    }
}

function Download-WithIWR([string]$Url, [string]$Destination) {
    try {
        $headers = @{
            'User-Agent'='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 SourceBackfill/1.0'
            'Accept'='application/pdf,application/zip,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*;q=0.8'
        }
        $resp = Invoke-WebRequest -Uri $Url -OutFile $Destination -Headers $headers -MaximumRedirection 10 -UseBasicParsing -TimeoutSec 900
        $ct = ''
        try { $ct = [string]$resp.Headers['Content-Type'] } catch {}
        return [pscustomobject]@{
            Ok = $true
            HttpStatus = [string]$resp.StatusCode
            ContentType = $ct
            EffectiveUrl = $Url
            Error = ''
            Warning = ''
            Method = 'Invoke-WebRequest'
            TlsValidation = 'WINDOWS_DEFAULT'
        }
    } catch {
        return [pscustomobject]@{
            Ok = $false
            HttpStatus = ''
            ContentType = ''
            EffectiveUrl = $Url
            Error = $_.Exception.Message
            Warning = ''
            Method = 'Invoke-WebRequest'
            TlsValidation = 'WINDOWS_DEFAULT'
        }
    }
}

if (-not (Test-Path -LiteralPath $RequestCsv)) {
    throw "No se encontro el CSV de solicitud: $RequestCsv"
}

$requested = Import-Csv -LiteralPath $RequestCsv -Encoding UTF8 | Where-Object { $Priorities -contains $_.priority }
if (-not $requested) { throw "No hay filas para las prioridades solicitadas: $($Priorities -join ', ')" }

$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$runDir = $OutputRoot
$filesDir = Join-Path $runDir 'files'
$rejectedDir = Join-Path $runDir 'rejected'
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
# Avoid stale files from a previous run being mistaken for this run.
Remove-Item -LiteralPath $filesDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $rejectedDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $filesDir -Force | Out-Null
New-Item -ItemType Directory -Path $rejectedDir -Force | Out-Null
Copy-Item -LiteralPath $RequestCsv -Destination (Join-Path $runDir 'SOURCE_BACKFILL_REQUEST_V96.csv') -Force

$results = New-Object System.Collections.Generic.List[object]
$total = @($requested).Count
$counter = 0

foreach ($row in $requested) {
    $counter++
    $gid = [int]$row.gap_id
    $entity = Get-SafeName $row.entity_or_id
    $ext = ([string]$row.extension).ToLowerInvariant()
    if (-not $ext.StartsWith('.')) { $ext = '.' + $ext }
    $name = ('{0:D3}_{1}_{2}{3}' -f $gid,$row.priority,$entity,$ext)
    $dest = Join-Path $filesDir $name
    Write-Host ("[{0}/{1}] {2} - {3}" -f $counter,$total,$row.priority,$row.entity_or_id) -ForegroundColor Cyan

    Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
    $download = Download-WithCurl $row.url $dest
    if ($null -eq $download -or -not $download.Ok) {
        if ($null -ne $download -and -not [string]::IsNullOrWhiteSpace($download.Error)) {
            Write-Host ("  curl fallo: {0}" -f $download.Error) -ForegroundColor DarkYellow
        }
        Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
        $download2 = Download-WithIWR $row.url $dest
        if ($null -eq $download) { $download = $download2 }
        elseif ($download2.Ok) { $download = $download2 }
        else {
            $download = [pscustomobject]@{
                Ok = $false
                HttpStatus = $download2.HttpStatus
                ContentType = $download2.ContentType
                EffectiveUrl = $download2.EffectiveUrl
                Error = ("curl: {0} | IWR: {1}" -f $download.Error,$download2.Error)
                Warning = $download.Warning
                Method = 'curl.exe + Invoke-WebRequest'
                TlsValidation = $download.TlsValidation
            }
        }
    }

    $status = 'DOWNLOAD_FAILED'
    $magicOk = $false
    $bytes = 0
    $sha = ''
    $finalName = ''

    if ($download.Ok -and (Test-Path -LiteralPath $dest)) {
        $fi = Get-Item -LiteralPath $dest
        $bytes = [int64]$fi.Length
        $magicOk = Test-Magic $dest $ext
        if ($magicOk) {
            $sha = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
            $status = 'DOWNLOAD_OK'
            $finalName = $name
            Write-Host ("  OK {0:N0} bytes  SHA256 {1}" -f $bytes,$sha) -ForegroundColor Green
        } else {
            $status = 'REJECTED_BAD_MAGIC'
            $reject = Join-Path $rejectedDir ($name + '.server-response')
            Move-Item -LiteralPath $dest -Destination $reject -Force
            $sha = (Get-FileHash -LiteralPath $reject -Algorithm SHA256).Hash.ToLowerInvariant()
            $finalName = 'rejected/' + [IO.Path]::GetFileName($reject)
            Write-Host '  RECHAZADO: la respuesta no coincide con el tipo de archivo esperado.' -ForegroundColor Red
        }
    } else {
        Remove-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
        $displayError = ''
        if ($null -ne $download -and $null -ne $download.Error) { $displayError = [string]$download.Error }
        Write-Host ("  FALLO: {0}" -f $displayError) -ForegroundColor Red
    }

    $results.Add([pscustomobject]@{
        gap_id = $gid
        priority = $row.priority
        entity_or_id = $row.entity_or_id
        role = $row.role
        url = $row.url
        expected_extension = $ext
        status = $status
        method = $download.Method
        tls_validation = $download.TlsValidation
        warning = $download.Warning
        http_status = $download.HttpStatus
        content_type = $download.ContentType
        effective_url = $download.EffectiveUrl
        local_filename = $finalName
        bytes = $bytes
        sha256 = $sha
        magic_ok = $magicOk
        retrieved_utc = [DateTime]::UtcNow.ToString('o')
        error = $download.Error
    })
}

$resultsCsv = Join-Path $runDir 'SOURCE_BACKFILL_RESULTS.csv'
$results | Export-Csv -LiteralPath $resultsCsv -NoTypeInformation -Encoding UTF8

$okCount = @($results | Where-Object {$_.status -eq 'DOWNLOAD_OK'}).Count
$failCount = $total - $okCount
$summary = @"
# Source backfill run V96

- UTC: $([DateTime]::UtcNow.ToString('o'))
- Priorities: $($Priorities -join ', ')
- Requested: $total
- DOWNLOAD_OK: $okCount
- Failed/rejected: $failCount

Subi el ZIP generado a ChatGPT para que los binarios validados se incorporen al repo acumulativo y se regenere el manifiesto SHA-256.
"@
Set-Content -LiteralPath (Join-Path $runDir 'README_RESULT.md') -Value $summary -Encoding UTF8

Get-ChildItem -LiteralPath $runDir -Filter 'SOURCE_BACKFILL_PAYLOAD_V96_*.zip' -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
$payload = Join-Path $runDir ("SOURCE_BACKFILL_PAYLOAD_V96_{0}.zip" -f $stamp)
Compress-Archive -Path (Join-Path $runDir '*') -DestinationPath $payload -CompressionLevel Optimal

Write-Host ''
Write-Host ('Terminado: {0}/{1} descargas validas.' -f $okCount,$total) -ForegroundColor Green
Write-Host ('Resultados: {0}' -f $runDir) -ForegroundColor Yellow
Write-Host ('Payload para subir: {0}' -f $payload) -ForegroundColor Yellow
if ($failCount -gt 0) {
    Write-Host 'Las fallidas quedan registradas en SOURCE_BACKFILL_RESULTS.csv; no se confunden con fuentes preservadas.' -ForegroundColor Yellow
}
