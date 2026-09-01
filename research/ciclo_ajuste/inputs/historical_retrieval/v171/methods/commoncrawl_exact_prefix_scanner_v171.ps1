param(
    [Parameter(Mandatory = $true)]
    [string]$Years,
    [Parameter(Mandatory = $true)]
    [string]$OutputCsv,
    [int]$RetryCount = 2,
    [int]$MaxTimeSeconds = 25,
    [switch]$RetryServiceErrors,
    [string]$CollectionIds = ''
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$catalogPath = Join-Path $PSScriptRoot '..\..\v170\binaries\commoncrawl_collection_catalog_2026_08_31.json'
$catalogPath = (Resolve-Path -LiteralPath $catalogPath).Path
$catalog = Get-Content -Raw -LiteralPath $catalogPath | ConvertFrom-Json
$yearTokens = @($Years.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$collections = @(
    $catalog |
        Where-Object {
            $idYear = ($_.id -replace '^CC-MAIN-', '').Substring(0, 4)
            $yearTokens -contains $idYear
        } |
        Select-Object -ExpandProperty id
)
if ($CollectionIds.Trim()) {
    $requestedCollections = @($CollectionIds.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    $collections = @($collections | Where-Object { $requestedCollections -contains $_ })
}
$targets = @(
    'www.sigen.gov.ar/documentacion/plananualpdfs/',
    'sigen.gov.ar/documentacion/plananualpdfs/'
)

$results = if (Test-Path -LiteralPath $OutputCsv) { @(Import-Csv -LiteralPath $OutputCsv) } else { @() }
foreach ($collection in $collections) {
    foreach ($target in $targets) {
        $prior = @($results | Where-Object { $_.collection -eq $collection -and $_.target -eq $target })
        if ($prior.Count -gt 0 -and -not ($RetryServiceErrors -and $prior[-1].classification -eq 'SERVICE_ERROR')) {
            continue
        }
        $encoded = [uri]::EscapeDataString($target)
        $uri = "https://index.commoncrawl.org/$collection-index?url=$encoded&matchType=prefix&output=json&filter=status%3A200"
        $classification = 'SERVICE_ERROR'
        $responseBody = ''
        $httpStatus = '000'
        $exitCode = -1
        $validRows = 0
        $attemptUsed = 0

        for ($attempt = 1; $attempt -le $RetryCount; $attempt++) {
            $attemptUsed = $attempt
            try {
                $raw = (& curl.exe --silent --show-error --location --max-time $MaxTimeSeconds --write-out "`n__HTTP_STATUS__=%{http_code}" $uri 2>&1 | Out-String).Trim()
                $exitCode = $LASTEXITCODE
            } catch {
                $exitCode = if ($LASTEXITCODE) { $LASTEXITCODE } else { -1 }
                $raw = $_.Exception.Message
            }
            $parts = $raw -split "`r?`n__HTTP_STATUS__=", 2
            $responseBody = $parts[0].Trim()
            $httpStatus = if ($parts.Count -eq 2) { $parts[1].Trim() } else { '000' }

            if ($exitCode -ne 0 -or $httpStatus -in @('000', '429', '500', '502', '503', '504') -or $responseBody -match '<html|Service Temporarily Unavailable|Bad Gateway') {
                $classification = 'SERVICE_ERROR'
                if ($attempt -lt $RetryCount) {
                    Start-Sleep -Milliseconds (1500 * $attempt)
                }
                continue
            }

            if ($httpStatus -eq '404' -and $responseBody -match 'No Captures found for:') {
                $classification = 'NO_CAPTURE_VALID'
                break
            }

            if ($httpStatus -ne '200') {
                $classification = 'UNEXPECTED_HTTP_RESPONSE'
                break
            }

            $lines = @($responseBody -split "`r?`n" | Where-Object { $_.Trim() })
            $parsed = @()
            $parseFailed = $false
            foreach ($line in $lines) {
                try {
                    $parsed += $line | ConvertFrom-Json
                } catch {
                    $parseFailed = $true
                    break
                }
            }
            if ($parseFailed -or $parsed.Count -eq 0) {
                $classification = 'INVALID_JSON_RESPONSE'
                break
            }

            $wrongPrefix = @($parsed | Where-Object {
                $url = [string]$_.url
                -not ($url.StartsWith("http://$target", [System.StringComparison]::OrdinalIgnoreCase) -or
                      $url.StartsWith("https://$target", [System.StringComparison]::OrdinalIgnoreCase))
            })
            if ($wrongPrefix.Count -gt 0) {
                $classification = 'CAPTURE_ROWS_WRONG_PREFIX'
                $validRows = $parsed.Count - $wrongPrefix.Count
            } else {
                $classification = 'CAPTURE_ROWS_VALID'
                $validRows = $parsed.Count
            }
            break
        }

        $result = [pscustomobject]@{
            collection = $collection
            year = ($collection -replace '^CC-MAIN-', '').Substring(0, 4)
            target = $target
            query_url = $uri
            attempts = $attemptUsed
            curl_exit = $exitCode
            http_status = $httpStatus
            classification = $classification
            valid_capture_rows = $validRows
            response = ($responseBody -replace "`r?`n", ' || ')
        }
        if ($prior.Count -gt 0) {
            $results = @($results | Where-Object { -not ($_.collection -eq $collection -and $_.target -eq $target) })
        }
        $results = @($results) + @($result)
        $outputParent = Split-Path -Parent $OutputCsv
        if ($outputParent) {
            New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
        }
        $results | Sort-Object collection, target | Export-Csv -LiteralPath $OutputCsv -NoTypeInformation -Encoding utf8
    }
}

$outputParent = Split-Path -Parent $OutputCsv
if ($outputParent) {
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}
$results | Sort-Object collection, target | Export-Csv -LiteralPath $OutputCsv -NoTypeInformation -Encoding utf8
$results | Group-Object classification | Sort-Object Name | Select-Object Name, Count
"years=$($yearTokens -join ',') collections=$($collections.Count) queries=$($results.Count)"
