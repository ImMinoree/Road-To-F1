$ErrorActionPreference = 'Stop'
$integrationRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$integrationEvidence = Join-Path $integrationRoot 'Evidence/Integration'
$integrationMap = Get-Content (Join-Path $integrationEvidence 'map_validation.json') -Raw | ConvertFrom-Json
if (-not $integrationMap.save_reload_passed -or $integrationMap.actors_preserved -ne 152 -or $integrationMap.grid_slots -ne 20) { throw 'Map preservation failed' }
$integrationAutomation = Get-Content (Join-Path $integrationEvidence 'Automation/index.json') -Raw | ConvertFrom-Json
if ($integrationAutomation.succeeded -ne 1 -or $integrationAutomation.failed -ne 0) { throw 'Ownership/steering/chassis test failed' }
$integrationPIE = Get-Content (Join-Path $integrationEvidence 'pie_confirmed.json') -Raw | ConvertFrom-Json
if (-not $integrationPIE.is_in_play_in_editor) { throw 'PIE was not confirmed' }
Add-Type -AssemblyName System.Drawing
$integrationShots = foreach ($integrationName in @('steering_left','steering_right','pre_start','driving','driving_later')) {
    $integrationData = Get-Content (Join-Path $integrationEvidence ($integrationName + '.json')) -Raw | ConvertFrom-Json
    if ($integrationData.world_type -ne 3 -or -not $integrationData.cockpit_active -or $integrationData.moved_early) { throw "Invalid PIE state: $integrationName" }
    if ($integrationName -in @('steering_left','steering_right','pre_start')) {
        if (-not $integrationData.gate_closed -or $integrationData.distance_cm -gt 1 -or $integrationData.start_events -ne 0) { throw "Gate failed: $integrationName" }
    } else {
        if ($integrationData.gate_closed -or $integrationData.start_events -ne 1 -or $integrationData.distance_cm -lt 500) { throw "Lights-out drive failed: $integrationName" }
    }
    if ($integrationName -eq 'pre_start' -and $integrationData.reds -ne 5) { throw 'Five-red-light capture missing' }
    $integrationFile = Join-Path $integrationEvidence ($integrationName + '.png')
    $integrationImage = [System.Drawing.Image]::FromFile($integrationFile)
    try {
        if ($integrationImage.Width -ne 1600 -or $integrationImage.Height -ne 900) { throw "Unexpected screenshot dimensions: $integrationName" }
        [ordered]@{ name=$integrationName; width=$integrationImage.Width; height=$integrationImage.Height; bytes=(Get-Item -LiteralPath $integrationFile).Length; telemetry=$integrationData }
    } finally { $integrationImage.Dispose() }
}
$integrationCurrent = Get-Content (Join-Path $integrationRoot 'Source/Road_To_F1_New/ProofPawn.cpp') -Raw
$integrationOriginal = (& git -C $integrationRoot show HEAD:Source/Road_To_F1_New/ProofPawn.cpp) -join "`n"
$integrationPattern = '(?s) Speed=FMath::Clamp\(Speed\+.*?else Reset\(\);'
if ([regex]::Match($integrationCurrent,$integrationPattern).Value.Replace("`r",'').Replace('GetSteeringYawRate()','65.f') -cne [regex]::Match($integrationOriginal,$integrationPattern).Value.Replace("`r",'')) { throw 'Movement formula changed beyond the approved shared steering parameter' }
$integrationResult = [ordered]@{ map=$integrationMap; automation_passed=$true; actual_pie=$true; movement_formula_preserved=$true; user_approved_shared_steering_parameter=$true; screenshots=$integrationShots; limitations=@('Prototype glove/sleeve art','Full-body rig is imported for AI opponents','Source wheels/linkages are static','Original sphere collision envelope retained; no new kart-extremity collision','See RacingAI evidence for subsequent full-lap tests; packaged build untested') }
$integrationResult | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $integrationEvidence 'results.json')
Write-Output 'PASS: saved map, original movement, hand/steering/chassis automation, held-throttle gate, one lights-out event, actual PIE driving and five valid 1600x900 screenshots.'
