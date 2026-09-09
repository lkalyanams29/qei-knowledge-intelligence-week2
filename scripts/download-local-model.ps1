$ErrorActionPreference='Stop'
$qeiRoot=Split-Path $PSScriptRoot -Parent
$modelDir=Join-Path $qeiRoot 'work\local-model'
New-Item -ItemType Directory -Force $modelDir | Out-Null
$releases=Invoke-RestMethod 'https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=10'
$release=$releases | Where-Object {($_.assets.name -match 'bin-win-cpu-x64.zip$').Count -gt 0} | Select-Object -First 1
$asset=$release.assets | Where-Object name -Match 'bin-win-cpu-x64.zip$' | Select-Object -First 1
if(-not $asset) {throw 'Official Windows CPU asset not found'}
$zip=Join-Path $modelDir 'llama.zip'
Invoke-WebRequest $asset.browser_download_url -OutFile $zip
if($asset.digest -and $asset.digest.StartsWith('sha256:')) {if((Get-FileHash $zip -Algorithm SHA256).Hash.ToLower() -ne $asset.digest.Substring(7)) {throw 'llama.cpp digest mismatch'}}
Expand-Archive -LiteralPath $zip -DestinationPath (Join-Path $modelDir 'runtime') -Force
$meta=Invoke-RestMethod 'https://huggingface.co/api/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF'
$file=$meta.siblings | Where-Object rfilename -eq 'qwen2.5-0.5b-instruct-q4_k_m.gguf' | Select-Object -First 1
if(-not $file) {throw 'Official Qwen model file not found'}
$revision=$meta.sha
$modelPath=Join-Path $modelDir $file.rfilename
Invoke-WebRequest "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/$revision/$($file.rfilename)" -OutFile $modelPath
Write-Output "Runtime: $($release.tag_name). Model revision: $revision"
Get-FileHash $modelPath -Algorithm SHA256 | Select-Object Hash,Path
