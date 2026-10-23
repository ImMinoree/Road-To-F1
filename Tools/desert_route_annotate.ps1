param([ValidateSet('Before','After')][string]$Phase='Before')
Add-Type -AssemblyName System.Drawing
$routeRoot=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$routeEvidence=Join-Path $routeRoot 'Evidence\DesertRoute'
$routeData=Get-Content (Join-Path $routeRoot 'Art\DesertRoute\audit.json') -Raw | ConvertFrom-Json
function MapPoint($p) { [System.Drawing.PointF]::new([single](1200+($p[1]+7000)*2400/33500),[single](1000-($p[0]-2500)*2400/33500)) }
foreach ($routeMap in @('DesertKarting','DesertKarting_Visual')) {
 $routeImage=Join-Path $routeEvidence "${Phase}_${routeMap}_TopDown.png"
 if (-not (Test-Path -LiteralPath $routeImage)) { continue }
 $routeBitmap=[System.Drawing.Bitmap]::new($routeImage)
 $routeGraphics=[System.Drawing.Graphics]::FromImage($routeBitmap)
 $routeGraphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
 $routeGraphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
 $routeFont=[System.Drawing.Font]::new('Segoe UI',25,[System.Drawing.FontStyle]::Bold)
 $routeSmall=[System.Drawing.Font]::new('Segoe UI',19)
 $routeWhite=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
 $routeBlack=[System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(225,15,25,35))
 $routeTeal=[System.Drawing.Color]::FromArgb(230,35,235,221)
 $routePen=[System.Drawing.Pen]::new($routeTeal,5)
 $routePoints=[System.Drawing.PointF[]]@($routeData.route_cm | ForEach-Object { MapPoint $_ })
 $routeGraphics.DrawPolygon($routePen,$routePoints)
 for ($ri=25;$ri -lt $routePoints.Length;$ri+=55) {
  $ra=$routePoints[$ri];$rb=$routePoints[($ri+3)%$routePoints.Length];$rdx=$rb.X-$ra.X;$rdy=$rb.Y-$ra.Y;$rl=[Math]::Sqrt($rdx*$rdx+$rdy*$rdy);$ux=$rdx/$rl;$uy=$rdy/$rl
  $routeArrow=[System.Drawing.PointF[]]@([System.Drawing.PointF]::new($ra.X+18*$ux,$ra.Y+18*$uy),[System.Drawing.PointF]::new($ra.X-11*$ux-10*$uy,$ra.Y-11*$uy+10*$ux),[System.Drawing.PointF]::new($ra.X-11*$ux+10*$uy,$ra.Y-11*$uy-10*$ux))
  $routeGraphics.FillPolygon([System.Drawing.SolidBrush]::new($routeTeal),$routeArrow)
 }
 function Label($text,$x,$y,$accent) {
  $size=$routeGraphics.MeasureString($text,$routeFont);$routeGraphics.FillRectangle($routeBlack,[single]($x-8),[single]($y-5),[single]($size.Width+16),[single]($size.Height+10));$routeGraphics.DrawString($text,$routeFont,[System.Drawing.SolidBrush]::new($accent),[single]$x,[single]$y)
 }
 $routeGold=[System.Drawing.Color]::FromArgb(255,255,222,65)
 foreach ($corner in $routeData.corners) {
  $p=MapPoint $corner.location_cm;$sgn=if ($p.X -lt 1200) {-1} else {1};$lx=$p.X+$sgn*62;if ($sgn -lt 0) {$lx-=45};$ly=$p.Y-45
  $routeGraphics.DrawLine([System.Drawing.Pen]::new($routeGold,3),$p.X,$p.Y,[single]($lx+20),[single]($ly+20));Label "C$($corner.number)" $lx $ly $routeGold
 }
 $sf=MapPoint $routeData.start_finish_cm
 $routeGraphics.DrawEllipse([System.Drawing.Pen]::new([System.Drawing.Color]::HotPink,7),[single]($sf.X-18),[single]($sf.Y-18),36,36)
 Label 'START / FINISH (existing gantry)' ($sf.X+32) ($sf.Y+20) ([System.Drawing.Color]::HotPink)
 $routeOrange=[System.Drawing.Color]::Orange
 for ($pi=0;$pi -lt 2;$pi++) {
  $p=MapPoint $routeData.pit_endpoints_cm[$pi];$name=if ($pi -eq 0) {'A: PROPOSED PIT ENTRY'} else {'B: PROPOSED PIT EXIT'}
  $routeGraphics.DrawEllipse([System.Drawing.Pen]::new($routeOrange,5),[single]($p.X-17),[single]($p.Y-17),34,34)
  Label $name ($p.X-485) ($p.Y-18) $routeOrange
 }
 $routeGraphics.FillRectangle($routeBlack,28,28,1020,180)
 $routeGraphics.DrawString('DESERT KARTING - VERIFIED SOURCE ROUTE',$routeFont,$routeWhite,48,43)
 $routeGraphics.DrawString('True orthographic Unreal capture; straight down, pitch -90 degrees.',$routeSmall,$routeWhite,48,90)
 $routeGraphics.DrawString('Arrows: source path order / confirmed +X main straight. Length: 1,040 m.',$routeSmall,$routeWhite,48,125)
 $routeGraphics.DrawString('C1-C7: analytical turn complexes; not official corner numbers.',$routeSmall,$routeWhite,48,160)
 $routeGraphics.FillRectangle($routeBlack,28,1810,1720,160)
 $routeGraphics.DrawString('PIT A/B ARE PROPOSALS - NO VERIFIED CONNECTORS',$routeFont,[System.Drawing.SolidBrush]::new($routeOrange),48,1825)
 $routeGraphics.DrawString('Pit junctions and original track geometry are unchanged. Outer access road is NOT the race route.',$routeSmall,$routeWhite,48,1870)
 $routeGraphics.DrawString('Infield/runoff remain drivable: off-track shortcuts are not physically prevented or race-enforced.',$routeSmall,$routeWhite,48,1905)
 $routeGraphics.Dispose();$routeOutput=Join-Path $routeEvidence "${Phase}_${routeMap}_Annotated.png";$routeBitmap.Save($routeOutput,[System.Drawing.Imaging.ImageFormat]::Png);$routeBitmap.Dispose()
 Write-Output $routeOutput
}
