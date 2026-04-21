[CmdletBinding()]
param(
    [string]$Distro = "Ubuntu-22.04",
    [string]$WorkspaceRoot = "/home/eric/workspace/data-security-lab2",
    [string]$SudoPassword = ""
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
$ScriptWsl = "$RepoRootWsl/scripts/wsl_setup_env.sh"
$CacheRoot = Join-Path (Split-Path -Parent $RepoRoot) "_wsl_cache"
$CacheRepo = Join-Path $CacheRoot "libsnark_abc-master"
$GitRewriteArg = 'url.https://github.com/.insteadOf=git://github.com/'
$CacheRepoWsl = ""

try {
    if (-not (Test-Path $CacheRepo)) {
        New-Item -ItemType Directory -Force -Path $CacheRoot | Out-Null
        Write-Host "Cloning Windows-side libsnark cache to $CacheRepo"
        & git -c $GitRewriteArg clone --recursive https://github.com/sec-bit/libsnark_abc.git $CacheRepo
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to clone Windows-side libsnark cache."
        }
    } else {
        Write-Host "Refreshing Windows-side libsnark submodules in $CacheRepo"
        & git -C $CacheRepo -c $GitRewriteArg submodule sync --recursive
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to sync Windows-side libsnark cache."
        }
        & git -C $CacheRepo -c $GitRewriteArg submodule update --init --recursive
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to refresh Windows-side libsnark cache."
        }
    }

    $CacheRepoWsl = Get-WslPath -WindowsPath $CacheRepo -DistroName $Distro
} catch {
    Write-Warning "Windows-side libsnark cache is unavailable. Falling back to direct WSL clone."
    Write-Warning $_.Exception.Message
    $CacheRepoWsl = ""
}

Write-Host "WSL repo root: $RepoRootWsl"
Write-Host "WSL workspace: $WorkspaceRoot"
if ($CacheRepoWsl) {
    Write-Host "Windows cache: $CacheRepo"
} else {
    Write-Host "Windows cache: unavailable, WSL will clone directly"
}

if ($SudoPassword) {
    & wsl -d $Distro -e sh $ScriptWsl $RepoRootWsl $WorkspaceRoot $SudoPassword $CacheRepoWsl
} else {
    & wsl -d $Distro -e sh $ScriptWsl $RepoRootWsl $WorkspaceRoot "" $CacheRepoWsl
}

if ($LASTEXITCODE -ne 0) {
    throw "WSL environment setup failed."
}
