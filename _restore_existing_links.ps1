$ErrorActionPreference = 'Stop'

$old = git show HEAD:DISCONNECTED_CATALOG.md
$oldStart = ($old | Select-String '^## Model Catalog for Azure Local Disconnected Operations').LineNumber
$oldEnd = ($old | Select-String '^## Agentic Retrieval on Foundry Local Extension Expansion Packs').LineNumber
$oldSec = $old[($oldStart + 2)..($oldEnd - 2)]

$oldMap = @{}
foreach ($line in $oldSec) {
    if ($line -like '|*') {
        $p = $line -split '\|'
        if ($p.Length -ge 7) {
            $alias = $p[1].Trim()
            $fw = $p[2].Trim()
            $comp = $p[3].Trim()
            $link = $p[6].Trim()
            if ($alias -and $fw -and $comp -and $link -and $link -ne '-' -and $alias -ne 'Alias') {
                $key = "$alias|$fw|$comp"
                $oldMap[$key] = $link
            }
        }
    }
}

$path = 'DISCONNECTED_CATALOG.md'
$cur = Get-Content $path
$start = ($cur | Select-String '^## Model Catalog for Azure Local Disconnected Operations').LineNumber
$end = ($cur | Select-String '^## Agentic Retrieval on Foundry Local Extension Expansion Packs').LineNumber

for ($i = $start + 2; $i -le $end - 2; $i++) {
    $line = $cur[$i - 1]
    if ($line -like '|*') {
        $p = $line -split '\|'
        if ($p.Length -ge 7) {
            $alias = $p[1].Trim()
            $fw = $p[2].Trim()
            $comp = $p[3].Trim()
            if ($alias -ne 'Alias') {
                $key = "$alias|$fw|$comp"
                if ($oldMap.ContainsKey($key)) {
                    $p[6] = ' ' + $oldMap[$key] + ' '
                    $cur[$i - 1] = ($p -join '|')
                }
            }
        }
    }
}

Set-Content -Path $path -Value $cur -Encoding UTF8

$new = Get-Content $path
$newStart = ($new | Select-String '^## Model Catalog for Azure Local Disconnected Operations').LineNumber
$newEnd = ($new | Select-String '^## Agentic Retrieval on Foundry Local Extension Expansion Packs').LineNumber
$newSec = $new[($newStart + 2)..($newEnd - 2)]

$preserved = 0
$total = 0
foreach ($line in $newSec) {
    if ($line -like '|*') {
        $p = $line -split '\|'
        if ($p.Length -ge 7) {
            $alias = $p[1].Trim()
            $fw = $p[2].Trim()
            $comp = $p[3].Trim()
            $lnk = $p[6].Trim()
            if ($alias -ne 'Alias') {
                $k = "$alias|$fw|$comp"
                if ($oldMap.ContainsKey($k)) {
                    $total++
                    if ($lnk -eq $oldMap[$k]) {
                        $preserved++
                    }
                }
            }
        }
    }
}

Write-Output "Old-link keys from HEAD: $($oldMap.Count)"
Write-Output "Preserved exact links in current file: $preserved / $total"
