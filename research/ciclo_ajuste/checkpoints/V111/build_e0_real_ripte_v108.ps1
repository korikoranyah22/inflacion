$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$checkpoint = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = (Resolve-Path (Join-Path $checkpoint '..\..\..\..')).Path
$ipcPath = Join-Path $repo 'research\ciclo_ajuste\inputs\historical_retrieval\v108\binaries\indec_ipc_gba_empalme_1943_2008.xls'
$outputPath = Join-Path $checkpoint 'E0_REAL_RIPTE_MONTHLY_V108.csv'
$invariant = [System.Globalization.CultureInfo]::InvariantCulture
$spanish = [System.Globalization.CultureInfo]::GetCultureInfo('es-AR')

$ripteCsv = @'
period,ripte_nominal_ars
2001-07,881.29
2001-08,879.63
2001-09,876.40
2001-10,880.26
2001-11,875.83
2001-12,870.52
2002-01,875.77
2002-02,887.02
2002-03,882.39
2002-04,882.13
2002-05,882.12
2002-06,874.52
2002-07,906.76
2002-08,885.30
2002-09,891.87
2002-10,900.78
2002-11,894.65
2002-12,900.69
2003-01,882.03
2003-02,890.60
2003-03,892.09
2003-04,889.92
2003-05,887.23
2003-06,903.82
2003-07,918.96
2003-08,941.34
2003-09,971.97
2003-10,1008.52
2003-11,1020.36
2003-12,1040.73
2004-01,1065.01
2004-02,1090.92
2004-03,1102.42
2004-04,1099.03
2004-05,1088.57
2004-06,1100.62
2004-07,1087.79
2004-08,1085.02
2004-09,1083.64
2004-10,1088.43
2004-11,1090.41
2004-12,1102.69
2005-01,1101.82
2005-02,1102.37
2005-03,1113.64
2005-04,1156.06
2005-05,1170.58
2005-06,1196.59
2005-07,1231.34
2005-08,1277.97
2005-09,1304.53
2005-10,1352.94
2005-11,1366.43
2005-12,1371.54
2006-01,1388.13
2006-02,1407.77
2006-03,1441.65
2006-04,1465.06
2006-05,1502.34
2006-06,1527.82
2006-07,1554.83
2006-08,1583.35
2006-09,1596.46
2006-10,1634.32
2006-11,1641.74
2006-12,1672.88
'@

$ripte = @{}
foreach ($row in ($ripteCsv | ConvertFrom-Csv)) {
    $ripte[$row.period] = [decimal]::Parse($row.ripte_nominal_ars, $invariant)
}

$connection = New-Object System.Data.OleDb.OleDbConnection("Provider=Microsoft.ACE.OLEDB.16.0;Data Source=$ipcPath;Extended Properties='Excel 8.0;HDR=No;IMEX=1'")
$connection.Open()
try {
    $command = $connection.CreateCommand()
    $command.CommandText = 'SELECT F1,F2,F3 FROM [Serie Histórica$]'
    $adapter = New-Object System.Data.OleDb.OleDbDataAdapter($command)
    $table = New-Object System.Data.DataTable
    [void]$adapter.Fill($table)
}
finally {
    $connection.Close()
}

$ipc = @{}
foreach ($row in $table.Rows) {
    $year = 0
    if ([int]::TryParse([string]$row[0], [ref]$year) -and $year -ge 2001 -and $year -le 2006) {
        $period = '{0}-{1:D2}' -f $year, [int]$row[1]
        $ipc[$period] = [decimal]::Parse([string]$row[2], $spanish)
    }
}

$baseDec = $ripte['2001-12'] / $ipc['2001-12']
$baseNov = $ripte['2001-11'] / $ipc['2001-11']
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('period,ripte_nominal_ars,ipc_gba_apr2008_100,real_ripte_dec2001_100,real_ripte_nov2001_100,dec2001_primary_recovery_flag,source_ripte_id,source_ipc_id,formula')

foreach ($period in ($ripte.Keys | Sort-Object)) {
    if (-not $ipc.ContainsKey($period)) { throw "Missing IPC for $period" }
    $real = ($ripte[$period] / $ipc[$period]) / $baseDec * [decimal]100
    $realNov = ($ripte[$period] / $ipc[$period]) / $baseNov * [decimal]100
    $flag = if ($period -lt '2001-12') { 'PRE_BASELINE' } elseif ($real -ge [decimal]100) { 'AT_OR_ABOVE_BASELINE' } else { 'BELOW_BASELINE' }
    $line = @(
        $period,
        $ripte[$period].ToString('0.00', $invariant),
        $ipc[$period].ToString('0.00000', $invariant),
        $real.ToString('0.000000', $invariant),
        $realNov.ToString('0.000000', $invariant),
        $flag,
        'e0_argentina_ripte_serie_junio_2026',
        'e0_indec_ipc_gba_empalme_1943_2008',
        '100*(RIPTE_t/IPC_t)/(RIPTE_base/IPC_base)'
    ) -join ','
    $lines.Add($line)
}

[System.IO.File]::WriteAllLines($outputPath, $lines, [System.Text.UTF8Encoding]::new($false))
Write-Output "Wrote $($ripte.Count) rows to $outputPath"
