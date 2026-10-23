Add-Type -AssemblyName System.Drawing
$taskDirectory = $PSScriptRoot
foreach ($view in @('front','side','top','three_quarter')) {
    $before = [System.Drawing.Image]::FromFile((Join-Path $taskDirectory "before_$view.png"))
    $after = [System.Drawing.Image]::FromFile((Join-Path $taskDirectory "refined_$view.png"))
    $canvas = [System.Drawing.Bitmap]::new(2000, 856)
    $graphics = [System.Drawing.Graphics]::FromImage($canvas)
    $graphics.Clear([System.Drawing.Color]::FromArgb(25,29,35))
    $font = [System.Drawing.Font]::new('Segoe UI', 18)
    $graphics.DrawString("BEFORE - $($view.Replace('_',' '))", $font, [System.Drawing.Brushes]::White, 20, 10)
    $graphics.DrawString('REFINED - existing tank adjusted in fitted copy', $font, [System.Drawing.Brushes]::White, 1020, 10)
    $graphics.DrawImage($before, 0, 56, 1000, 800)
    $graphics.DrawImage($after, 1000, 56, 1000, 800)
    $canvas.Save((Join-Path $taskDirectory "comparison_$view.png"), [System.Drawing.Imaging.ImageFormat]::Png)
    $font.Dispose(); $graphics.Dispose(); $canvas.Dispose(); $before.Dispose(); $after.Dispose()
}
