param([ValidateSet('Balanced','Validation')][string]$Profile='Balanced')
$circuitProject = Join-Path $PSScriptRoot '..\Road_To_F1_New.uproject'
$circuitQuality = if ($Profile -eq 'Validation') { 3 } else { 2 }
$circuitResolution = if ($Profile -eq 'Validation') { 100 } else { 75 }
$circuitCommands = "sg.ViewDistanceQuality $circuitQuality,sg.AntiAliasingQuality $circuitQuality,sg.ShadowQuality $circuitQuality,sg.GlobalIlluminationQuality $circuitQuality,sg.ReflectionQuality $circuitQuality,sg.TextureQuality $circuitQuality,r.ScreenPercentage $circuitResolution"
& 'D:\Boring\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' $circuitProject '/Game/RoadToF1/Maps/CircuitDevelopment' -game -windowed -ResX=1920 -ResY=1080 "-ExecCmds=$circuitCommands"
