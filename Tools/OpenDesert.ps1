param([ValidateSet('Balanced','Validation')][string]$Profile='Balanced',[switch]$Editor)
$desertProject = Join-Path $PSScriptRoot '..\Road_To_F1_New.uproject'
$desertQuality = if ($Profile -eq 'Validation') { 3 } else { 2 }
$desertResolution = if ($Profile -eq 'Validation') { 100 } else { 75 }
$desertCommands = "sg.ViewDistanceQuality $desertQuality,sg.AntiAliasingQuality $desertQuality,sg.ShadowQuality $desertQuality,sg.GlobalIlluminationQuality $desertQuality,sg.ReflectionQuality $desertQuality,sg.TextureQuality $desertQuality,r.ScreenPercentage $desertResolution"
$desertArgs = @($desertProject,'/Game/RoadToF1/Maps/DesertKarting','-windowed','-ResX=1920','-ResY=1080',"-ExecCmds=$desertCommands")
if (-not $Editor) { $desertArgs += '-game' }
& 'D:\Boring\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' @desertArgs
