param([int]$WaitForCapturePid=0,[switch]$VariantOnly)
$visualRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$visualEvidence = Join-Path $visualRoot 'Evidence\DesertVisual'
$visualExe = 'D:\Boring\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$visualProject = Join-Path $visualRoot 'Road_To_F1_New.uproject'
if ($WaitForCapturePid) { while (Get-Process -Id $WaitForCapturePid -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 2 } }
$visualPrevious = Join-Path $visualRoot 'Evidence\Runtime.json'
$visualBackup = Join-Path $visualEvidence 'runtime_preserved.json'
if (Test-Path -LiteralPath $visualPrevious) { Copy-Item -LiteralPath $visualPrevious -Destination $visualBackup }
try {
 $visualTests = if ($VariantOnly) { @('Visual') } else { @('Baseline','Visual') }
 foreach ($visualTest in $visualTests) {
  $visualMap = if ($visualTest -eq 'Baseline') { '/Game/RoadToF1/Maps/DesertKarting' } else { '/Game/RoadToF1/Maps/DesertKarting_Visual?game=/Script/Road_To_F1_New.ProofGameMode' }
  $visualStart = Get-Date
  $visualArgs = @($visualProject,$visualMap,'-game','-windowed','-ResX=1920','-ResY=1080','-ProofSmokeTest','-unattended','-nosplash','-nosound','-NoLiveCoding','-sm6','-csvCaptureFrames=1200','-csvCompression=0','-csvGpuStats','-ExecCmds="sg.ViewDistanceQuality 2,sg.AntiAliasingQuality 2,sg.ShadowQuality 2,sg.GlobalIlluminationQuality 2,sg.ReflectionQuality 2,sg.TextureQuality 2,r.ScreenPercentage 75,r.VSync 0,t.MaxFPS 0"',"-abslog=$visualEvidence\runtime_$visualTest.log")
  $visualProcess = Start-Process -FilePath $visualExe -WindowStyle Hidden -ArgumentList $visualArgs -PassThru
  Wait-Process -Id $visualProcess.Id
  if ((Get-Item -LiteralPath $visualPrevious).LastWriteTime -lt $visualStart) { throw "No fresh driving test report: $visualTest" }
  Copy-Item -LiteralPath $visualPrevious -Destination (Join-Path $visualEvidence "runtime_$visualTest.json")
  $visualCsv = Get-ChildItem (Join-Path $visualRoot 'Saved\Profiling\CSV') -Filter '*.csv' -ErrorAction SilentlyContinue | Where-Object LastWriteTime -ge $visualStart | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($visualCsv) { Copy-Item -LiteralPath $visualCsv.FullName -Destination (Join-Path $visualEvidence "profile_$visualTest.csv") }
  $visualCsvLog = Select-String -LiteralPath (Join-Path $visualEvidence "runtime_$visualTest.log") -Pattern 'Writing CSV to file : (.+\.csv)' | Select-Object -Last 1
  if ($visualCsvLog) { $visualCsvPath = $visualCsvLog.Matches[0].Groups[1].Value.Trim(); if (Test-Path -LiteralPath $visualCsvPath) { Copy-Item -LiteralPath $visualCsvPath -Destination (Join-Path $visualEvidence "profile_$visualTest.csv") } }
  Get-Content (Join-Path $visualEvidence "runtime_$visualTest.json")
 }
 if (-not $VariantOnly) {
  $visualArgs = @($visualProject,'/Game/RoadToF1/Maps/DesertKarting_Visual','-game','-windowed','-ResX=1280','-ResY=720','-unattended','-nosplash','-nosound','-NoLiveCoding','-benchmark','-seconds=5','-fps=60','-ExecCmds="getall Pawn Name"',"-abslog=$visualEvidence\environment_preview.log")
  $visualProcess = Start-Process -FilePath $visualExe -WindowStyle Hidden -ArgumentList $visualArgs -PassThru
  Wait-Process -Id $visualProcess.Id
 }
} finally {
 if (Test-Path -LiteralPath $visualBackup) { Copy-Item -LiteralPath $visualBackup -Destination $visualPrevious }
}
