param([switch]$Editor)
$integratedProject = (Resolve-Path (Join-Path $PSScriptRoot '../Road_To_F1_New.uproject')).Path
$integratedArgs = @($integratedProject, '/Game/RoadToF1/Maps/DesertKarting_Visual', '-windowed', '-ResX=1600', '-ResY=900', '-nosplash')
if (-not $Editor) { $integratedArgs += '-game' }
& 'D:/Boring/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' @integratedArgs
