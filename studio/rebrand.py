#!/usr/bin/env python3
"""Apply the sharek (Creative Studio) branding on top of upstream FigCraft.

Only user-visible text is rebranded; crate names, the file format (`.figcraft`), settings folders
and the copyright and licence lines keep their upstream names, so `git merge upstream/main` stays
easy. The script is idempotent: after merging upstream, resolve any conflicts in favour of upstream
and run it again.

    python3 studio/rebrand.py

The Share ▸ Online default is changed here too: the built-in server is empty (see RULES), so a
build without FIGCRAFT_DEFAULT_SERVER never sends files to collab.craftapps.dev.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arabic_names  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / 'docs/studio/sharek.svg'
NAME = 'sharek'
ARABIC = 'شارك'
UP = 'FigCraft'
REPO = 'https://github.com/7mz410/CreativeStudio-sharek'
SITE = 'https://studio.creative.ps'
APP_SITE = 'https://sharek.studio.creative.ps'
BUNDLE = 'ps.creative.studio.sharek'
ABOUT_OLD = ('Interface design and prototyping. A free, open-source, clean-room design tool written from scratch in '
             'Rust, part of the ArtCraft Crafting Apps.')
ABOUT_NEW = f'Part of the Creative Studio suite. Built on {UP} by the ArtCraft team.'
# Text kept as upstream wrote it: credits, copyright, the licence line and the settings folders.
KEEP = (
    'by the ArtCraft team', 'the FigCraft authors', 'FigCraft contributors', 'FigCraft authors',
    'Application Support/FigCraft', 'C:\\Apps\\FigCraft', 'Programs\\FigCraft', 'Program Files\\FigCraft',
)
# Whole files whose FigCraft literals are settings-folder names, not visible text.
SKIP_FILES = ('apps/figcraft/src/services.rs', 'crates/mcp/src/server.rs')

# (file, upstream text, our text). Applied first, before the general rename.
RULES = [
    ('crates/ui-egui/src/dialogs.rs',
     f'        "{ABOUT_OLD}",',
     f'        "{ABOUT_NEW}",'),
    ('crates/ui-egui/src/dialogs.rs',
     '    ui.hyperlink_to("getartcraft.com/apps/figcraft", "https://getartcraft.com/apps/figcraft");',
     f'    ui.hyperlink_to("{NAME}.studio.creative.ps", "{APP_SITE}");'),
    ('crates/ui-egui/src/dialogs.rs',
     '    ui.hyperlink_to(tr("Join us on Discord"), "https://discord.gg/artcraft");',
     f'    ui.hyperlink_to(tr("Source code on GitHub"), "{REPO}");'),
    ('crates/ui-egui/src/lib.rs',
     '"open.help" => self.services.open_url("https://getartcraft.com/apps/figcraft"),',
     f'"open.help" => self.services.open_url("{APP_SITE}"),'),
    ('crates/engine/src/live.rs',
     '    None => "wss://collab.craftapps.dev/",',
     '    None => "",'),
    ('apps/figcraft/build.rs',
     '        res.set("CompanyName", "ArtCraft");',
     '        res.set("CompanyName", "Creative Studio");'),
    ('packaging/macos/Info.plist.in',
     '<string>ai.storyteller.figcraft</string>',
     f'<string>{BUNDLE}</string>'),
    ('packaging/linux/ai.storyteller.figcraft.desktop',
     'Name=FigCraft',
     f'Name={NAME}'),
    ('packaging/linux/ai.storyteller.figcraft.metainfo.xml.in',
     '<name>FigCraft</name>',
     f'<name>{NAME}</name>'),
    ('packaging/windows/figcraft.wxs',
     'Name="FigCraft"',
     f'Name="{NAME}"'),
    # Right-to-left interface (studio/RTL.md): vendor/egui is upstream egui 0.36.2 plus the marked
    # changes. lib.rs turns the switch on each frame for Arabic and mirrors the side panels.
    ('Cargo.toml',
     '[workspace]\nresolver = "3"\n',
     '[patch.crates-io]\n# Creative Studio: egui with a right-to-left switch for the Arabic interface (studio/RTL.md).\negui = { path = "vendor/egui" }\n\n[workspace]\nresolver = "3"\n'),
    ('crates/ui-egui/src/lib.rs',
     '        theme::set_doc_profile(&ctx, self.session.doc().map_or(figcraft_color::ColorProfile::Srgb, |d| d.color_profile));\n',
     '        // Creative Studio: the Arabic interface lays out right to left (studio/RTL.md).\n        egui::set_rtl(i18n::is_rtl());\n        theme::set_doc_profile(&ctx, self.session.doc().map_or(figcraft_color::ColorProfile::Srgb, |d| d.color_profile));\n'),
    ('crates/ui-egui/src/lib.rs',
     '''            egui::Panel::left("left_rail")
                .exact_size(56.0)''',
     '''            // Creative Studio: the start side is the right one in the Arabic interface.
            let start = if egui::is_rtl() { egui::Panel::right("left_rail") } else { egui::Panel::left("left_rail") };
            start
                .exact_size(56.0)'''),
    ('crates/ui-egui/src/lib.rs',
     '''        if left_open {
            edges.push(("left", ui.available_rect_before_wrap().min.x + left_w, left_w, 1.0));
            egui::Panel::left("left_panel")
                .resizable(false)''',
     '''        let rtl = egui::is_rtl();
        if left_open {
            let avail = ui.available_rect_before_wrap();
            let (x, grows) = if rtl { (avail.max.x - left_w, -1.0) } else { (avail.min.x + left_w, 1.0) };
            edges.push(("left", x, left_w, grows));
            let panel = if rtl { egui::Panel::right("left_panel") } else { egui::Panel::left("left_panel") };
            panel
                .resizable(false)'''),
    ('crates/ui-egui/src/lib.rs',
     '''            edges.push(("right", ui.available_rect_before_wrap().max.x - right_w, right_w, -1.0));
            egui::Panel::right("right_panel")
                .resizable(false)''',
     '''            let avail = ui.available_rect_before_wrap();
            let (x, grows) = if rtl { (avail.min.x + right_w, 1.0) } else { (avail.max.x - right_w, -1.0) };
            edges.push(("right", x, right_w, grows));
            let panel = if rtl { egui::Panel::left("right_panel") } else { egui::Panel::right("right_panel") };
            panel
                .resizable(false)'''),
    # The mark: the sharek star (studio_mark.rs, generated from docs/studio/sharek.svg) replaces
    # FigCraft's chameleon tail in the Logo icon, which the About tile, the dock and the rail draw.
    ('crates/ui-egui/src/lib.rs',
     'pub mod style_picker;\n',
     'pub mod studio_mark;\npub mod style_picker;\n'),
    ('crates/ui-egui/src/icons.rs',
     '''        Logo => {
            // FigCraft's own mark: the curled tail of the chameleon on the app icon. One bold
            // stroke: a shaft along the bottom, then three half turns, each tighter than the last.
            let mut tail = vec![(13.75, 13.0)];
            tail.extend(arc_pts(7.25, 8.0, 5.0, FRAC_PI_2, 3.0 * FRAC_PI_2));
            tail.extend(arc_pts(7.25, 6.5, 3.5, 3.0 * FRAC_PI_2, 5.0 * FRAC_PI_2));
            tail.extend(arc_pts(7.25, 8.25, 1.75, FRAC_PI_2, 3.0 * FRAC_PI_2));
            let v: Vec<Pos2> = tail.iter().map(|&(x, y)| p.raw(x, y)).collect();
            p.painter.add(Shape::line(v, Stroke::new(1.7 * p.s, p.color)));
            p.dot(13.75, 13.0, 0.85);
            p.dot(7.25, 6.5, 0.85);
        }''',
     '''        Logo => {
            // Creative Studio: the sharek star, in its own colours (studio_mark.rs).
            crate::studio_mark::paint(p.painter, egui::Rect::from_min_size(p.o, egui::vec2(16.0 * p.s, 16.0 * p.s)));
        }'''),
    # About: the star is navy and red, so its tile is white (as on the suite's cards).
    ('crates/ui-egui/src/dialogs.rs',
     'use crate::theme::{ACCENT, Tokens, regular, semibold};',
     'use crate::theme::{Tokens, regular, semibold};'),
    ('crates/ui-egui/src/dialogs.rs',
     '''        ui.painter().rect_filled(r, CornerRadius::same(10), ACCENT);
        icons::paint(ui.painter(), r.shrink(10.0), Icon::Logo, Color32::WHITE);''',
     '''        ui.painter().rect_filled(r, CornerRadius::same(10), Color32::WHITE);
        icons::paint(ui.painter(), r.shrink(10.0), Icon::Logo, Color32::WHITE);'''),
]

# The locale catalogs: the About text is a new key (its English is the new text; other
# languages fall back to English until translated), and the Discord key goes.
LOCALE_DROP = ('"Join us on Discord" =', f'"{ABOUT_OLD}" =')
LOCALE_ADD_EN = [
    f'"{ABOUT_NEW}" = "{ABOUT_NEW}"',
    '"Source code on GitHub" = "Source code on GitHub"',
]

STRING = re.compile(r'"(?:[^"\\\n]|\\.)*"')
# Rust sources whose string literals are shown to the user (the engine, the UI, the apps).
RUST_DIRS = ('crates/ui-egui/src', 'crates/engine/src', 'crates/mcp/src', 'apps')


def rename(lit: str) -> str:
    if any(k in lit for k in KEEP):
        return lit
    return lit.replace(UP, NAME)


def renamed_code(text: str) -> str:
    return STRING.sub(lambda m: rename(m.group(0)), text)


def apply_rules() -> list:
    changed = []
    for rel, a, b in RULES:
        p = ROOT / rel
        s = p.read_text(encoding='utf-8')
        if b in s:
            continue  # already applied
        if a not in s:
            print(f'warning: {rel}: upstream text not found (did upstream change it?): {a[:70]!r}')
            continue
        p.write_text(s.replace(a, b, 1), encoding='utf-8')
        changed.append(rel)
    return changed


def rename_sources() -> list:
    changed = []
    files = []
    for d in RUST_DIRS:
        files += sorted((ROOT / d).rglob('*.rs'))
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        # Tests keep upstream's wording; the shipped code and its visible strings are renamed.
        if p.name.endswith('_tests.rs') or p.name == 'tests.rs' or '/tests/' in rel or rel in SKIP_FILES:
            continue
        s = p.read_text(encoding='utf-8')
        o = renamed_code(s)
        if o != s:
            p.write_text(o, encoding='utf-8')
            changed.append(rel)
    # Visible HTML of the web build (title and loading text).
    p = ROOT / 'apps/figcraft-web/index.html'
    s = p.read_text(encoding='utf-8')
    o = s.replace('<title>FigCraft</title>', f'<title>{NAME}</title>').replace('Loading FigCraft&hellip;', f'Loading {NAME}&hellip;')
    if o != s:
        p.write_text(o, encoding='utf-8')
        changed.append('apps/figcraft-web/index.html')
    # Locale catalogs: keys and values alike (the key is the English text the code writes).
    for p in sorted((ROOT / 'crates/ui-egui/locales').glob('*.toml')):
        s = p.read_text(encoding='utf-8')
        lines = []
        for line in s.split('\n'):
            if line.startswith(LOCALE_DROP):
                continue
            # The About line keeps FigCraft in every language (its values name the ArtCraft team too).
            lines.append(line if 'Built on FigCraft' in line else renamed_code(line))
        o = '\n'.join(lines)
        if p.stem == 'en':
            for add in LOCALE_ADD_EN:
                if add.split(' = ')[0] not in o:
                    o = _insert_after_ui(o, add)
        if o != s:
            p.write_text(o, encoding='utf-8')
            changed.append(p.relative_to(ROOT).as_posix())
    # macOS bundle: the names shown in Finder and the Dock; the executable stays `figcraft`.
    plist = ROOT / 'packaging/macos/Info.plist.in'
    s = plist.read_text(encoding='utf-8')
    o = re.sub(r'(<key>CFBundle(?:Display)?Name</key>\s*<string>)FigCraft(</string>)', rf'\g<1>{NAME}\2', s)
    # Document type names show in Finder; the executable and the .icns file keep package.sh's names.
    o = re.sub(r'(<key>(?:CFBundleTypeName|UTTypeDescription)</key>\s*<string>)FigCraft( Document)?(</string>)',
               lambda m: f'{m.group(1)}{NAME}{m.group(2) or ""}{m.group(3)}', o)
    if o != s:
        plist.write_text(o, encoding='utf-8')
        changed.append('packaging/macos/Info.plist.in')
    # Windows installer: visible names only. UpgradeCode and registry keys stay upstream's.
    wxs = ROOT / 'packaging/windows/figcraft.wxs'
    s = wxs.read_text(encoding='utf-8')
    o = s.replace('Title="FigCraft"', f'Title="{NAME}"').replace('Description="FigCraft interface design and prototyping tool"',
                                                              f'Description="{NAME} interface design and prototyping tool"')
    o = o.replace('Name="FigCraft"', f'Name="{NAME}"')
    if o != s:
        wxs.write_text(o, encoding='utf-8')
        changed.append('packaging/windows/figcraft.wxs')
    return changed


# ---- The mark ---------------------------------------------------------------------------------
# docs/studio/sharek.svg is two filled outlines (a navy star and a red star), one closed contour each.
# The generator flattens each contour's curves into points and ear-clips it into triangles, so the
# app paints the mark as plain egui meshes (no SVG parser in the app, and egui fills only convex
# polygons). The output is studio/../crates/ui-egui/src/studio_mark.rs.
MARK_OUT = ROOT / 'crates/ui-egui/src/studio_mark.rs'
_NUM = re.compile(r'[MLCZ]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?')


def _contours(d: str) -> list:
    """Absolute M, L, C and Z path data as closed point lists (curves sampled)."""
    toks = _NUM.findall(d)
    out, cur, cmd, i, pos = [], [], None, 0, (0.0, 0.0)
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == 'Z':
                if cur:
                    out.append(cur)
                cur = []
            continue
        if cmd == 'M':
            if cur:
                out.append(cur)
            pos = (float(toks[i]), float(toks[i + 1]))
            cur, i, cmd = [pos], i + 2, 'L'
        elif cmd == 'L':
            pos = (float(toks[i]), float(toks[i + 1]))
            cur.append(pos)
            i += 2
        elif cmd == 'C':
            c1, c2, end = [(float(toks[i + k]), float(toks[i + k + 1])) for k in (0, 2, 4)]
            for n in range(1, 13):
                t_ = n / 12
                mt = 1 - t_
                cur.append(tuple(mt ** 3 * pos[j] + 3 * mt * mt * t_ * c1[j] + 3 * mt * t_ * t_ * c2[j] + t_ ** 3 * end[j] for j in (0, 1)))
            pos = end
            i += 6
        else:
            raise ValueError(f'mark path: command {cmd!r} not handled')
    if cur:
        out.append(cur)
    return [c[:-1] if len(c) > 1 and c[-1] == c[0] else c for c in out]


def _cross(o, a, b) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _ear_clip(pts: list) -> list:
    """Triangles (index triples) of a simple polygon."""
    idx = list(range(len(pts)))
    if sum(_cross((0, 0), pts[idx[i - 1]], pts[idx[i]]) for i in range(len(idx))) < 0:
        idx.reverse()  # counter-clockwise: a convex corner has a positive cross product
    tris = []
    while len(idx) > 3:
        n = len(idx)
        for i in range(n):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % n]
            pa, pb, pc = pts[a], pts[b], pts[c]
            if _cross(pa, pb, pc) <= 0:
                continue
            inside = any(
                _cross(pa, pb, pts[j]) >= 0 and _cross(pb, pc, pts[j]) >= 0 and _cross(pc, pa, pts[j]) >= 0
                for j in idx if j not in (a, b, c) and pts[j] not in (pa, pb, pc))
            if inside:
                continue
            tris.append((a, b, c))
            del idx[i]
            break
        else:
            raise ValueError('mark outline: ear clipping found no ear (self-intersecting?)')
    tris.append(tuple(idx))
    return tris


def write_mark() -> bool:
    svg = LOGO.read_text(encoding='utf-8')
    _, _, w, h = (float(x) for x in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
    fills = dict(re.findall(r'\.(cls-\d+)\s*\{\s*fill:\s*#([0-9a-fA-F]{6})', svg))
    rows = []
    for attrs in re.findall(r'<path\b([^>]*)>', svg):
        cls = re.search(r'class="(cls-\d+)"', attrs).group(1)
        d = re.search(r'\sd="([^"]+)"', attrs).group(1)
        contours = _contours(d)
        if len(contours) != 1:
            raise ValueError(f'mark path has {len(contours)} contours; one closed outline per path is expected')
        pts = contours[0]
        tris = _ear_clip(pts)
        c = fills[cls]
        rgb = ', '.join(str(int(c[i:i + 2], 16)) for i in (0, 2, 4))
        pts_s = ', '.join(f'[{x:.3f}, {y:.3f}]' for x, y in pts)
        tri_s = ', '.join(f'[{a}, {b}, {c_}]' for a, b, c_ in tris)
        rows.append(f'    (&[{pts_s}], &[{tri_s}], [{rgb}]),')
    out = ('//! Creative Studio: the sharek star (docs/studio/sharek.svg), generated by studio/rebrand.py.\n'
           '//! The outline points and their triangles are precomputed, so drawing needs no path parser.\n\n'
           f'/// The artwork size (its viewBox).\npub const SIZE: (f32, f32) = ({w:g}, {h:g});\n\n'
           '/// Each shape: its outline points (artwork units), triangles over them, and its fill colour.\n'
           'type Shape = (&\'static [[f32; 2]], &\'static [[u32; 3]], [u8; 3]);\n\n'
           'pub const SHAPES: &[Shape] = &[\n'
           + '\n'.join(rows) + '\n];\n\n'
           '/// Paint the mark in `rect`: whole, centred, aspect kept, in its own colours.\n'
           'pub fn paint(painter: &egui::Painter, rect: egui::Rect) {\n'
           '    let (w, h) = SIZE;\n'
           '    let k = (rect.width() / w).min(rect.height() / h);\n'
           '    let o = rect.center() - egui::vec2(w * k / 2.0, h * k / 2.0);\n'
           '    for &(points, triangles, [r, g, b]) in SHAPES {\n'
           '        let mut mesh = egui::Mesh::default();\n'
           '        for &[x, y] in points {\n'
           '            mesh.colored_vertex(o + egui::vec2(x * k, y * k), egui::Color32::from_rgb(r, g, b));\n'
           '        }\n'
           '        for &[a, b, c] in triangles {\n'
           '            mesh.add_triangle(a, b, c);\n'
           '        }\n'
           '        painter.add(egui::Shape::mesh(mesh));\n'
           '    }\n'
           '}\n')
    # Compare as rustfmt would write it, so `cargo fmt` and this script agree.
    out = subprocess.run(['rustfmt', '--edition', '2024', '--emit', 'stdout', '--config-path', str(ROOT)], input=out, capture_output=True, text=True).stdout or out
    if MARK_OUT.exists() and MARK_OUT.read_text(encoding='utf-8') == out:
        return False
    MARK_OUT.write_text(out, encoding='utf-8')
    return True


def _insert_after_ui(text: str, line: str) -> str:
    """Put a new key just after the Dual-licence line, which sits in the [ui] table."""
    marker = '"Dual-licensed MIT OR Apache-2.0.'
    out = []
    done = False
    for ln in text.split('\n'):
        out.append(ln)
        if not done and ln.startswith(marker):
            out.append(line)
            done = True
    return '\n'.join(out)


def main():
    changed = apply_rules() + rename_sources()
    if write_mark():
        changed.append('crates/ui-egui/src/studio_mark.rs')
    changed += arabic_names.apply(ROOT, NAME, ARABIC)
    for c in sorted({str(c.relative_to(ROOT)) if isinstance(c, Path) else c for c in changed}):
        print('rebranded', c)


if __name__ == '__main__':
    main()
