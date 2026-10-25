param([switch]$Legacy,[switch]$Capture)
$kartProject=(Resolve-Path (Join-Path $PSScriptRoot '../Road_To_F1_New.uproject')).Path
$kartArgs=@($kartProject,'/Game/RoadToF1/Maps/DesertKarting_Visual','-game','-ResX=1600','-ResY=900','-windowed','-nosplash')
if($Legacy){$kartArgs+='-CockpitBefore'}
if($Capture){$kartArgs+='-CockpitReferenceCapture'}
& 'D:\Boring\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' @kartArgs
