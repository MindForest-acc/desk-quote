import AppKit

/// 生成 App 图标：宣纸底 + 朱砂闲章「案头」。
/// 用与卡片同一套颜色和字体，图标和产品是同一件东西。
func draw(_ side: CGFloat) -> NSImage {
    let img = NSImage(size: NSSize(width: side, height: side))
    img.lockFocus()
    let r = NSRect(x: 0, y: 0, width: side, height: side)
    let radius = side * 0.2237                       // macOS 圆角矩形比例

    let paper = NSBezierPath(roundedRect: r, xRadius: radius, yRadius: radius)
    paper.addClip()
    NSGradient(colors: [NSColor(srgbRed: 0.965, green: 0.945, blue: 0.905, alpha: 1),
                        NSColor(srgbRed: 0.898, green: 0.863, blue: 0.800, alpha: 1)])?
        .draw(in: r, angle: -90)

    // 纸纹
    for _ in 0 ..< Int(side * 22) {
        let a = Double.random(in: 0.02 ... 0.10)
        NSColor(white: Bool.random() ? 0 : 1, alpha: a).set()
        NSRect(x: .random(in: 0 ..< side), y: .random(in: 0 ..< side),
               width: side / 340, height: side / 340).fill()
    }

    // 朱砂闲章：竖排「案头」
    let s = side * 0.46
    let seal = NSRect(x: (side - s) / 2, y: (side - s * 1.24) / 2, width: s, height: s * 1.24)
    NSColor(srgbRed: 0.639, green: 0.180, blue: 0.137, alpha: 0.94).set()
    NSBezierPath(roundedRect: seal, xRadius: s * 0.1, yRadius: s * 0.1).fill()

    let font = NSFont(name: "STLibianSC-Regular", size: s * 0.62)
        ?? NSFont.systemFont(ofSize: s * 0.62)
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font, .foregroundColor: NSColor(srgbRed: 0.965, green: 0.945, blue: 0.905, alpha: 1),
    ]
    for (i, ch) in "案头".enumerated() {
        let str = NSAttributedString(string: String(ch), attributes: attrs)
        let sz = str.size()
        str.draw(at: NSPoint(x: seal.midX - sz.width / 2,
                             y: seal.maxY - s * 0.66 * CGFloat(i + 1) - s * 0.06))
    }
    img.unlockFocus()
    return img
}

let out = URL(fileURLWithPath: CommandLine.arguments[1])
try? FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
for px in [16, 32, 64, 128, 256, 512, 1024] {
    let img = draw(CGFloat(px))
    guard let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff) else { continue }
    rep.size = NSSize(width: px, height: px)
    let name = px <= 512 ? "icon_\(px)x\(px).png" : "icon_512x512@2x.png"
    try? rep.representation(using: .png, properties: [:])!
        .write(to: out.appendingPathComponent(name))
    if px >= 32, px <= 512 {
        try? rep.representation(using: .png, properties: [:])!
            .write(to: out.appendingPathComponent("icon_\(px/2)x\(px/2)@2x.png"))
    }
}
print("iconset → \(out.path)")
