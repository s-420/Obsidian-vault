$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$python = (Get-Command python -ErrorAction Stop).Source
$venv = Join-Path $project '.build-venv'
if (-not (Test-Path -LiteralPath $venv)) {
    & $python -m venv $venv
}
$pip = Join-Path $venv 'Scripts\pip.exe'
$py = Join-Path $venv 'Scripts\python.exe'
& $pip install --disable-pip-version-check pyinstaller python-docx pillow
& $py -m PyInstaller --noconfirm --clean --onefile --windowed --name 'Scribe文档转换器' --collect-all docx --collect-all PIL (Join-Path $project 'scribe_converter.py') --distpath (Join-Path $project 'dist') --workpath (Join-Path $project 'work\pyinstaller') --specpath (Join-Path $project 'work')
Compress-Archive -LiteralPath (Join-Path $project 'dist\Scribe文档转换器.exe'), (Join-Path $project '使用说明.md') -DestinationPath (Join-Path $project 'dist\Scribe文档转换器-便携版.zip') -Force
Write-Output "构建完成：$(Join-Path $project 'dist')"
