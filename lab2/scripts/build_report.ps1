[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ReportDir = Join-Path (Split-Path -Parent $PSScriptRoot) "report"
$MainTex = Join-Path $ReportDir "main.tex"
$NeedsBibtex = Select-String -Path $MainTex -Pattern '\\bibliography\s*\{' -Quiet

Push-Location $ReportDir
try {
    & xelatex main.tex
    if ($LASTEXITCODE -ne 0) { throw "xelatex pass 1 failed" }

    if ($NeedsBibtex) {
        & bibtex main
        if ($LASTEXITCODE -ne 0) { throw "bibtex failed" }
    }

    & xelatex main.tex
    if ($LASTEXITCODE -ne 0) { throw "xelatex pass 2 failed" }

    & xelatex main.tex
    if ($LASTEXITCODE -ne 0) { throw "xelatex pass 3 failed" }
}
finally {
    Pop-Location
}

Write-Host "Report built at $ReportDir\\main.pdf"
