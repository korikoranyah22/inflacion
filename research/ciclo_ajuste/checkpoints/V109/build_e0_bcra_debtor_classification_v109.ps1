$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$checkpoint = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = (Resolve-Path (Join-Path $checkpoint '..\..\..\..')).Path
$sourcePath = Join-Path $repo 'data\fuentes\ciclo_ajuste\backfill_v96_round2\hist_bcra_baldethis.xls'
$outputPath = Join-Path $checkpoint 'E0_BCRA_DEBTOR_CLASSIFICATION_MONTHLY_V109.csv'
$invariant = [System.Globalization.CultureInfo]::InvariantCulture
$spanish = [System.Globalization.CultureInfo]::GetCultureInfo('es-AR')

function Convert-SourceNumber {
    param([object]$Value)
    if ($null -eq $Value -or $Value -is [DBNull]) { return $null }
    $text = ([string]$Value).Trim()
    if (-not $text -or $text -eq '.') { return $null }
    if ($text -match '^[-+]?\d{1,3}(\.\d{3})+$') {
        return [decimal]::Parse($text.Replace('.', ''), $invariant)
    }
    if ($text.Contains(',')) {
        return [decimal]::Parse($text, $spanish)
    }
    return [decimal]::Parse($text, $invariant)
}

function Format-Number {
    param([object]$Value, [string]$Pattern)
    if ($null -eq $Value) { return '' }
    return ([decimal]$Value).ToString($Pattern, $invariant)
}

$monthMap = @{
    'Ene.' = 1; 'Feb.' = 2; 'Mar.' = 3; 'Abr.' = 4; 'May.' = 5; 'Jun.' = 6
    'Jul.' = 7; 'Ago.' = 8; 'Set.' = 9; 'Oct.' = 10; 'Nov.' = 11; 'Dic.' = 12
}

$connection = New-Object System.Data.OleDb.OleDbConnection("Provider=Microsoft.ACE.OLEDB.16.0;Data Source=$sourcePath;Extended Properties='Excel 8.0;HDR=No;IMEX=1'")
$connection.Open()
try {
    $command = $connection.CreateCommand()
    $command.CommandText = 'SELECT * FROM [Detalle$]'
    $adapter = New-Object System.Data.OleDb.OleDbDataAdapter($command)
    $table = New-Object System.Data.DataTable
    [void]$adapter.Fill($table)
}
finally {
    $connection.Close()
}

$header = @(
    'period','source_excel_row','source_status',
    'total_financing_thousand_ars','total_normal_pct','total_potential_risk_pct',
    'total_problem_component_1_pct','total_problem_component_2_pct',
    'total_high_risk_component_1_pct','total_high_risk_component_2_pct',
    'total_irrecoverable_uncollectible_pct','total_irrecoverable_technical_pct',
    'total_irregular_situations_3_to_6_pct','total_irregular_residual_pct','total_rounding_delta_pct',
    'private_financing_thousand_ars','private_normal_pct','private_potential_risk_pct',
    'private_problem_component_1_pct','private_problem_component_2_pct',
    'private_high_risk_component_1_pct','private_high_risk_component_2_pct',
    'private_irrecoverable_uncollectible_pct','private_irrecoverable_technical_pct',
    'private_irregular_situations_3_to_6_pct','private_irregular_residual_pct','private_rounding_delta_pct',
    'source_id','source_sheet','definition'
) -join ','
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add($header)

for ($rowIndex = 0; $rowIndex -lt $table.Rows.Count; $rowIndex++) {
    $row = $table.Rows[$rowIndex]
    $year = 0
    $monthText = ([string]$row[1]).Trim()
    if (-not [int]::TryParse(([string]$row[0]).Trim(), [ref]$year)) { continue }
    if ($year -lt 2001 -or $year -gt 2003 -or -not $monthMap.ContainsKey($monthText)) { continue }
    $period = '{0}-{1:D2}' -f $year, $monthMap[$monthText]

    $total = Convert-SourceNumber $row[54]
    $totalNormal = Convert-SourceNumber $row[55]
    $totalPotential = Convert-SourceNumber $row[56]
    $totalBuckets = @(57,58,59,60,61,62) | ForEach-Object { Convert-SourceNumber $row[$_] }
    $private = Convert-SourceNumber $row[81]
    $privateNormal = Convert-SourceNumber $row[82]
    $privatePotential = Convert-SourceNumber $row[83]
    $privateBuckets = @(84,85,86,87,88,89) | ForEach-Object { Convert-SourceNumber $row[$_] }

    if ($null -eq $total) {
        $status = 'PUBLISHED_AS_DOT'
        $totalIrregular = $null
        $totalResidual = $null
        $totalDelta = $null
        $privateIrregular = $null
        $privateResidual = $null
        $privateDelta = $null
    }
    else {
        $status = 'AVAILABLE'
        $totalIrregular = [decimal]0
        foreach ($value in $totalBuckets) { $totalIrregular += $value }
        $totalResidual = [decimal]100 - $totalNormal - $totalPotential
        $totalDelta = $totalIrregular - $totalResidual
        $privateIrregular = [decimal]0
        foreach ($value in $privateBuckets) { $privateIrregular += $value }
        $privateResidual = [decimal]100 - $privateNormal - $privatePotential
        $privateDelta = $privateIrregular - $privateResidual
    }

    $values = [System.Collections.Generic.List[string]]::new()
    $values.Add($period)
    $values.Add([string]($rowIndex + 1))
    $values.Add($status)
    $values.Add((Format-Number $total '0'))
    $values.Add((Format-Number $totalNormal '0.000000'))
    $values.Add((Format-Number $totalPotential '0.000000'))
    foreach ($value in $totalBuckets) { $values.Add((Format-Number $value '0.000000')) }
    $values.Add((Format-Number $totalIrregular '0.000000'))
    $values.Add((Format-Number $totalResidual '0.000000'))
    $values.Add((Format-Number $totalDelta '0.000000'))
    $values.Add((Format-Number $private '0'))
    $values.Add((Format-Number $privateNormal '0.000000'))
    $values.Add((Format-Number $privatePotential '0.000000'))
    foreach ($value in $privateBuckets) { $values.Add((Format-Number $value '0.000000')) }
    $values.Add((Format-Number $privateIrregular '0.000000'))
    $values.Add((Format-Number $privateResidual '0.000000'))
    $values.Add((Format-Number $privateDelta '0.000000'))
    $values.Add('hist_bcra_baldethis')
    $values.Add('Detalle')
    $values.Add('irregular=sum of source classification components for situations 3 to 6; not a payment-arrears-only measure')
    $lines.Add(($values -join ','))
}

if ($lines.Count -ne 37) { throw "Expected header plus 36 monthly rows; found $($lines.Count)" }
[System.IO.File]::WriteAllLines($outputPath, $lines, [System.Text.UTF8Encoding]::new($false))
Write-Output "Wrote 36 rows to $outputPath"
