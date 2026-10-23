Add-Type -AssemblyName System.Drawing
$taskDirectory = $PSScriptRoot
$v2Directory = Join-Path (Split-Path -Parent $taskDirectory) 'Refinement_v2'
foreach ($view in @('front','side','three_quarter')) {
    $before = [System.Drawing.Image]::FromFile((Join-Path $v2Directory "refined_$view.png"))
    $after = [System.Drawing.Image]::FromFile((Join-Path $taskDirectory "reclined_$view.png"))
    $canvas = [System.Drawing.Bitmap]::new(2000, 856)
    $graphics = [System.Drawing.Graphics]::FromImage($canvas)
    $graphics.Clear([System.Drawing.Color]::FromArgb(25,29,35))
    $font = [System.Drawing.Font]::new('Segoe UI', 18)
    $graphics.DrawString("V2 BEFORE - $($view.Replace('_',' '))", $font, [System.Drawing.Brushes]::White, 20, 10)
    $graphics.DrawString('V3 RECLINE - tank and controls unchanged', $font, [System.Drawing.Brushes]::White, 1020, 10)
    $graphics.DrawImage($before, 0, 56, 1000, 800); $graphics.DrawImage($after, 1000, 56, 1000, 800)
    $canvas.Save((Join-Path $taskDirectory "comparison_$view.png"), [System.Drawing.Imaging.ImageFormat]::Png)
    $font.Dispose(); $graphics.Dispose(); $canvas.Dispose(); $before.Dispose(); $after.Dispose()
}
