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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arabic_names  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
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
            lines.append(renamed_code(line))
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
    changed += arabic_names.apply(ROOT, NAME, ARABIC)
    for c in sorted({str(c.relative_to(ROOT)) if isinstance(c, Path) else c for c in changed}):
        print('rebranded', c)


if __name__ == '__main__':
    main()
