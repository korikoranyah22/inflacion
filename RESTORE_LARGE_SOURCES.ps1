$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Manifest = Join-Path $Root 'research\ciclo_ajuste\source_audit\GITHUB_LARGE_SOURCE_PACKING_V96.csv'
$rows = Import-Csv -LiteralPath $Manifest -Encoding UTF8
foreach ($row in $rows) {
    $archive = Join-Path $Root ($row.archive_path -replace '/', '\')
    $target = Join-Path $Root ($row.original_path -replace '/', '\')
    if (!(Test-Path -LiteralPath $archive)) { throw "Falta archive: $archive" }
    $archiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
    if ($archiveHash -ne $row.archive_sha256.ToLowerInvariant()) { throw "SHA archive incorrecto: $archive" }
    $destDir = Split-Path -Parent $target
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    $tmp = Join-Path $env:TEMP ("v96_restore_" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        Expand-Archive -LiteralPath $archive -DestinationPath $tmp -Force
        $extracted = Join-Path $tmp $row.archive_member
        if (!(Test-Path -LiteralPath $extracted)) { throw "No se extrajo $($row.archive_member)" }
        $rawHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $extracted).Hash.ToLowerInvariant()
        if ($rawHash -ne $row.original_sha256.ToLowerInvariant()) { throw "SHA original incorrecto: $($row.archive_member)" }
        Move-Item -LiteralPath $extracted -Destination $target -Force
        Write-Host ("OK  {0}  ({1} bytes)" -f $row.original_path,$row.original_bytes) -ForegroundColor Green
    } finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host 'Restauracion completa. Los originales estan gitignored; los ZIP son los archivos versionados.' -ForegroundColor Cyan
