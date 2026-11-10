$ErrorActionPreference = "Stop"

$source = (Resolve-Path $PSScriptRoot).Path
$destination = Join-Path (Split-Path $source -Parent) "engineering_portfolio.zip"
if (Test-Path $destination) {
    throw "Refusing to overwrite existing archive: $destination"
}

Compress-Archive -Path (Join-Path $source "*") -DestinationPath $destination
Write-Output "Created $destination"
