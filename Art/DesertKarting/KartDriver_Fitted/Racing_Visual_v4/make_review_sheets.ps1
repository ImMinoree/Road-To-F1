Add-Type -AssemblyName System.Drawing
$outDir = $PSScriptRoot
$bitmap = New-Object System.Drawing.Bitmap 1600,1360
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::FromArgb(22,24,28))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font = New-Object System.Drawing.Font 'Arial',17
$names = @('front','side','rear','three_quarter')
for ($idx=0; $idx -lt 4; $idx++) {
    $picture = [System.Drawing.Image]::FromFile((Join-Path $outDir ('racer_' + $names[$idx] + '.png')))
    $left = ($idx % 2) * 800
    $top = [math]::Floor($idx / 2) * 680
    $graphics.DrawString(('V4 Cycles - ' + $names[$idx]),$font,[System.Drawing.Brushes]::White,$left+16,$top+9)
    $graphics.DrawImage($picture,[int]$left,[int]($top+40),800,640)
    $picture.Dispose()
}
$bitmap.Save((Join-Path $outDir 'views_contact_sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
$bitmap = New-Object System.Drawing.Bitmap 1800,800
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::FromArgb(22,24,28))
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$referencePath = 'C:/Users/GBURG-4/AppData/Local/Temp/codex-clipboard-61f53560-1267-4120-b813-bc1340be994f.png'
$paths = @($referencePath,(Join-Path $outDir 'racer_three_quarter.png'))
$labels = @('Supplied reference','Actual V4 model - realism target NOT achieved')
for ($idx=0; $idx -lt 2; $idx++) {
    $picture = [System.Drawing.Image]::FromFile($paths[$idx])
    $scale = [math]::Min(900/$picture.Width,740/$picture.Height)
    $width = [int]($picture.Width*$scale)
    $height = [int]($picture.Height*$scale)
    $left = [int]($idx*900+(900-$width)/2)
    $top = [int](50+(740-$height)/2)
    $graphics.DrawString($labels[$idx],$font,[System.Drawing.Brushes]::White,($idx*900+12),12)
    $graphics.DrawImage($picture,$left,$top,$width,$height)
    $picture.Dispose()
}
$bitmap.Save((Join-Path $outDir 'reference_comparison.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$font.Dispose(); $graphics.Dispose(); $bitmap.Dispose()
