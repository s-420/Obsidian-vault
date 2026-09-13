param(
    [Parameter(Position=0)]
    [string]$InputFile
)

$ErrorActionPreference = 'Stop'
$app = Join-Path $PSScriptRoot 'dist\Scribe文档转换器.exe'
if (-not (Test-Path -LiteralPath $app)) {
    throw "未找到程序：$app"
}
if ([string]::IsNullOrWhiteSpace($InputFile)) {
    & $app --gui
} else {
    & $app $InputFile
}
