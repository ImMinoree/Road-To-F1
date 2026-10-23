param([switch]$Capture)
$kartProject = (Resolve-Path (Join-Path $PSScriptRoot '../Road_To_F1_New.uproject')).Path
$kartEditor = 'D:\Boring\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$kartArguments = @($kartProject, '-game', '-ResX=1280', '-ResY=720', '-windowed', '-nosplash')
if ($Capture) { $kartArguments += '-KartFPCapture' }
& $kartEditor @kartArguments
