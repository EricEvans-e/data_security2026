[CmdletBinding()]
param(
    [int]$X = 3,
    [int]$Out = 35,
    [string]$Distro = "Ubuntu-22.04",
    [string]$WorkspaceRoot = "/home/eric/workspace/data-security-lab2"
)

$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Get-WslPath {
    param(
        [Parameter(Mandatory = $true)][string]$WindowsPath,
        [Parameter(Mandatory = $true)][string]$DistroName
    )

    $lines = & wsl -d $DistroName -e wslpath -a $WindowsPath 2>$null
    $pathLine = $lines | Where-Object { $_ -match '^/' } | Select-Object -Last 1
    if (-not $pathLine) {
        throw "Failed to convert Windows path to WSL path: $WindowsPath"
    }
    return $pathLine.Trim()
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RepoRootWsl = Get-WslPath -WindowsPath $RepoRoot -DistroName $Distro
$ScriptWsl = "$RepoRootWsl/scripts/wsl_run_demo.sh"

Write-Host "Running demo with x=$X, out=$Out"
& wsl -d $Distro -e sh $ScriptWsl $RepoRootWsl $WorkspaceRoot $X $Out

if ($LASTEXITCODE -ne 0) {
    throw "Lab2 demo run failed."
}
