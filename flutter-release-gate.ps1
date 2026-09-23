[CmdletBinding()]
param(
    [string]$Project = '.',
    [switch]$SkipRestore
)

$ErrorActionPreference = 'Stop'
$projectPath = (Resolve-Path -LiteralPath $Project).Path

function Invoke-Checked {
    param([string]$Name, [scriptblock]$Command)
    Write-Host "==> $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

Push-Location $projectPath
try {
    if (-not $SkipRestore) {
        Invoke-Checked 'Flutter dependency restore' { flutter pub get }
    }
    Invoke-Checked 'Flutter localization generation' { flutter gen-l10n }
    Invoke-Checked 'Dart formatting verification' { dart format --output=none --set-exit-if-changed . }
    Invoke-Checked 'Flutter analyzer' { flutter analyze }
    Invoke-Checked 'Flutter tests' { flutter test --exclude-tags=platform-golden }
}
finally {
    Pop-Location
}
