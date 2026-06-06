// Generates a 1024x1024 Family Calculator app icon in Bluestem brand colors.
// Usage: swiftc icon.swift -o /tmp/makeicon && /tmp/makeicon out.png
import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let W = 1024, H = 1024
let cs = CGColorSpaceCreateDeviceRGB()
guard let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8,
                          bytesPerRow: 0, space: cs,
                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else {
    FileHandle.standardError.write("context failed\n".data(using: .utf8)!); exit(1)
}

func c(_ r: Double, _ g: Double, _ b: Double, _ a: Double = 1) -> CGColor {
    CGColor(red: r/255, green: g/255, blue: b/255, alpha: a)
}
func rr(_ rect: CGRect, _ radius: CGFloat) -> CGPath {
    CGPath(roundedRect: rect, cornerWidth: radius, cornerHeight: radius, transform: nil)
}

ctx.clear(CGRect(x: 0, y: 0, width: W, height: H))

// Background squircle with a navy -> deep-navy vertical gradient.
let bg = CGRect(x: 100, y: 100, width: 824, height: 824)
ctx.saveGState()
ctx.addPath(rr(bg, 184)); ctx.clip()
let grad = CGGradient(colorsSpace: cs,
                      colors: [c(46, 134, 193), c(27, 79, 114)] as CFArray,
                      locations: [0, 1])!
ctx.drawLinearGradient(grad, start: CGPoint(x: 0, y: 924), end: CGPoint(x: 0, y: 100), options: [])
ctx.restoreGState()

// Calculator display (light blue) near the top of the inner area.
let disp = CGRect(x: 210, y: 664, width: 604, height: 150)
ctx.addPath(rr(disp, 30)); ctx.setFillColor(c(214, 232, 245)); ctx.fillPath()

// 3x3 key grid. Cream keys, with the bottom-right key in russet as the accent.
let g: CGFloat = 34
let keyW = (604 - 2*g)/3
let keyH = (414 - 2*g)/3
let startX: CGFloat = 210
let topY: CGFloat = 624          // top edge of the key area
for row in 0..<3 {
    for col in 0..<3 {
        let x = startX + CGFloat(col)*(keyW + g)
        let y = topY - keyH - CGFloat(row)*(keyH + g)
        let accent = (row == 2 && col == 2)
        ctx.addPath(rr(CGRect(x: x, y: y, width: keyW, height: keyH), 22))
        ctx.setFillColor(accent ? c(187, 120, 120) : c(250, 250, 247))
        ctx.fillPath()
    }
}

guard let img = ctx.makeImage() else { exit(1) }
let outPath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "icon.png"
let url = URL(fileURLWithPath: outPath) as CFURL
guard let dest = CGImageDestinationCreateWithURL(url, UTType.png.identifier as CFString, 1, nil) else { exit(1) }
CGImageDestinationAddImage(dest, img, nil)
if !CGImageDestinationFinalize(dest) { exit(1) }
