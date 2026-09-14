import AppKit
import SwiftUI

/// 离屏渲染若干张卡片为 PNG。用于设计迭代与交付验收，
/// 不依赖录屏权限，也不需要把 App 摆到屏幕上去截图。
let corpus = Corpus.load()
let outDir = URL(fileURLWithPath: CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : ".")

func render(_ quote: Quote, dark: Bool, note: Bool, scale: CGFloat = 2) -> NSImage {
    let theme = Theme.of(book: quote.book, dark: dark)
    let vertical = TextLayout.fitsVertical(quote.text)
    let view = CardView(quote: quote, book: corpus.book(of: quote), theme: theme,
                        vertical: vertical, showNote: note,
                        isFavorite: false, width: 340,
                        onNext: {}, onToggleNote: {}, onToggleFavorite: {})
        .padding(26)                        // 留出投影余量
    let host = NSHostingView(rootView: view)
    host.layoutSubtreeIfNeeded()
    host.frame = NSRect(origin: .zero, size: host.fittingSize)
    guard let rep = host.bitmapImageRepForCachingDisplay(in: host.bounds) else {
        fatalError("无法为 \(quote.text.prefix(8)) 创建位图")
    }
    rep.size = NSSize(width: host.bounds.width, height: host.bounds.height)
    host.cacheDisplay(in: host.bounds, to: rep)
    let img = NSImage(size: rep.size)
    img.addRepresentation(rep)
    _ = scale
    return img
}

func save(_ img: NSImage, _ name: String) {
    guard let tiff = img.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:]) else { return }
    try? png.write(to: outDir.appendingPathComponent(name))
    print("  \(name)  \(Int(img.size.width))×\(Int(img.size.height))")
}

/// 每本书各取一条短句（触发竖排）和一条长句（横排）
let picks: [(String, Bool)] = [
    ("sunzi", true), ("sunzi", false),
    ("zhuangzi", true), ("zhuangzi", false),
    ("mozi", true), ("mozi", false),
    ("yangming", true), ("yangming", false),
    ("maoxuan", true), ("maoxuan", false),
]
for (book, wantVertical) in picks {
    let pool = corpus.quotes.filter {
        $0.book == book && TextLayout.fitsVertical($0.text) == wantVertical
    }
    guard let q = pool.randomElement() else { continue }
    let tag = wantVertical ? "竖" : "横"
    save(render(q, dark: false, note: true), "\(book)-\(tag)-light.png")
    save(render(q, dark: true, note: true), "\(book)-\(tag)-dark.png")
}
print("完成 → \(outDir.path)")
