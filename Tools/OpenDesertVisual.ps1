param([ValidateSet('Balanced','Validation')][string]$Profile='Balanced',[switch]$Editor,[switch]$Drive)
$visualProject = Join-Path $PSScriptRoot '..\Road_To_F1_New.uproject'
$visualQuality = if ($Profile -eq 'Validation') { 3 } else { 2 }
$visualResolution = if ($Profile -eq 'Validation') { 100 } else { 75 }
$visualMap = '/Game/RoadToF1/Maps/DesertKarting_Visual'
if ($Drive) { $visualMap += '?game=/Script/Road_To_F1_New.ProofGameMode' }
$visualCommands = "sg.ViewDistanceQuality $visualQuality,sg.AntiAliasingQuality $visualQuality,sg.ShadowQuality $visualQuality,sg.GlobalIlluminationQuality $visualQuality,sg.ReflectionQuality $visualQuality,sg.TextureQuality $visualQuality,r.ScreenPercentage $visualResolution"
$visualArgs = @($visualProject,$visualMap,'-windowed','-ResX=1920','-ResY=1080',"-ExecCmds=$visualCommands")
if (-not $Editor) { $visualArgs += '-game' }
& 'D:\Boring\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' @visualArgs
