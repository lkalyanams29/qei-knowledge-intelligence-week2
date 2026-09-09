param([Parameter(Mandatory=$true)][string]$TextPath,[Parameter(Mandatory=$true)][string]$OutputPath)
$qeiVoice = New-Object -ComObject SAPI.SpVoice
$qeiVoice.Rate = 0
$qeiStream = New-Object -ComObject SAPI.SpFileStream
$qeiStream.Open($OutputPath, 3, $false)
$qeiVoice.AudioOutputStream = $qeiStream
[void]$qeiVoice.Speak([System.IO.File]::ReadAllText($TextPath))
$qeiStream.Close()
