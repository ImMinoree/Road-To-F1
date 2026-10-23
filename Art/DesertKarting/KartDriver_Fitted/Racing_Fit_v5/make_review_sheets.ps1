Add-Type -AssemblyName System.Drawing
$outDir=$PSScriptRoot
$font=New-Object System.Drawing.Font 'Arial',16
function Make-Sheet($items,$columns,$target) {
    $rows=[int][math]::Ceiling($items.Count/$columns)
    $bitmap=New-Object System.Drawing.Bitmap ($columns*600),($rows*520)
    $g=[System.Drawing.Graphics]::FromImage($bitmap)
    $g.Clear([System.Drawing.Color]::FromArgb(22,24,28))
    $g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    for ($idx=0;$idx -lt $items.Count;$idx++) {
        $item=$items[$idx]
        $image=[System.Drawing.Image]::FromFile((Join-Path $outDir $item.File))
        $x=($idx % $columns)*600
        $y=[int][math]::Floor($idx/$columns)*520
        $g.DrawString($item.Label,$font,[System.Drawing.Brushes]::White,($x+10),($y+9))
        $g.DrawImage($image,$x,($y+40),600,480)
        $image.Dispose()
    }
    $bitmap.Save((Join-Path $outDir $target),[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose();$bitmap.Dispose()
}
$items=@(
    @{File='steering_left.png';Label='Left: -25 degrees'},
    @{File='steering_center.png';Label='Center: 0 degrees'},
    @{File='steering_right.png';Label='Right: +25 degrees'},
    @{File='side.png';Label='V5 side - centered steering'},
    @{File='three_quarter.png';Label='V5 three-quarter - centered steering'},
    @{File='grip_center.png';Label='Actual modeled glove / rim contact'}
)
Make-Sheet $items 3 'V5_Review.png'
$items=@(
    @{File='grip_left.png';Label='Grip inspection: left -25'},
    @{File='grip_center.png';Label='Grip inspection: center'},
    @{File='grip_right.png';Label='Grip inspection: right +25'}
)
Make-Sheet $items 3 'V5_Grip_Review.png'
$items=@(
    @{File='../Racing_Visual_v4/racer_side.png';Label='V4 before: original fitted copy'},
    @{File='side.png';Label='V5 after: same kart and camera'}
)
Make-Sheet $items 2 'V4_V5_side_comparison.png'
$font.Dispose()
