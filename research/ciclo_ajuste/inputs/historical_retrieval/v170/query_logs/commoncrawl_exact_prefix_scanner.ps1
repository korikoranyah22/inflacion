param(
    [Parameter(Mandatory = $true)]
    [string]$Years,
    [Parameter(Mandatory = $true)]
    [string]$OutputCsv
)

$ErrorActionPreference = 'Stop'
$catalogPath = Join-Path $PSScriptRoot 'v170_commoncrawl_collections.json'
$catalog = Get-Content -Raw -LiteralPath $catalogPath | ConvertFrom-Json
$yearTokens = @($Years.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$collections = @(
    $catalog |
        Where-Object { $idYear = ($_.id -replace '^CC-MAIN-','').Substring(0,4); $yearTokens -contains $idYear } |
        Select-Object -ExpandProperty id
)

$targets = @(
    'www.sigen.gov.ar/documentacion/plananualpdfs/',
    'sigen.gov.ar/documentacion/plananualpdfs/'
)
$jobs = foreach ($collection in $collections) {
    foreach ($target in $targets) {
        [pscustomobject]@{ collection = $collection; target = $target }
    }
}

$results = $jobs | ForEach-Object -Parallel {
    $collection = $_.collection
    $target = $_.target
    $encoded = [uri]::EscapeDataString($target)
    $uri = "https://index.commoncrawl.org/$collection-index?url=$encoded&matchType=prefix&output=json&filter=status%3A200"
    $body = (& curl.exe --silent --show-error --location --max-time 12 $uri 2>&1 | Out-String).Trim()
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0 -or $body -match '503 Service Temporarily Unavailable' -or $body -match '502 Bad Gateway') {
        $classification = 'SERVICE_ERROR'
    } elseif ($body -match 'No Captures found') {
        $classification = 'NO_CAPTURE'
    } elseif ($body) {
        $classification = 'CAPTURE_ROWS'
    } else {
        $classification = 'EMPTY_RESPONSE'
    }
    [pscustomobject]@{
        collection = $collection
        target = $target
        query_url = $uri
        curl_exit = $exitCode
        classification = $classification
        response = ($body -replace "`r?`n", ' || ')
    }
} -ThrottleLimit 8

$results | Sort-Object collection | Export-Csv -LiteralPath $OutputCsv -NoTypeInformation -Encoding utf8
$results | Group-Object classification | Sort-Object Name | Select-Object Name,Count
"years=$($yearTokens -join ',') collections=$($collections.Count) queries=$($jobs.Count)"
