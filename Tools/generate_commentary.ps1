# Regenerate the temporary local speech clips; replace with recorded WAVs for final voice.
$ErrorActionPreference = 'Stop'
$taskRepo = Split-Path -Parent $PSScriptRoot
$taskAudio = Join-Path $taskRepo 'Art/Audio/Commentary'
$taskLines = Get-Content -LiteralPath (Join-Path $taskAudio 'lines.json') -Raw | ConvertFrom-Json
$taskVoice = New-Object -ComObject SAPI.SpVoice
foreach ($taskLine in $taskLines.PSObject.Properties) {
    $taskStream = New-Object -ComObject SAPI.SpFileStream
    $taskStream.Format.Type = 22 # 22050Hz, mono, 16bit
    $taskStream.Open((Join-Path $taskAudio ($taskLine.Name + '.wav')), 3, $false)
    try {
        $taskVoice.AudioOutputStream = $taskStream
        $taskVoice.Rate = 1
        $null = $taskVoice.Speak($taskLine.Value)
    } finally { $taskStream.Close() }
}
Write-Output ('Generated using ' + $taskVoice.Voice.GetDescription())
