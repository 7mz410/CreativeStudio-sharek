# Right-to-left interface (sharek)

When the interface language is Arabic, sharek lays its panels out right to left: the layers rail
and the Layers panel sit on the right, the Design and Prototype panel on the left. Rows and menus
run from the right. The canvas, rulers and artwork are not mirrored, and neither is the floating
tool bar over the canvas.

## How it works

egui lays everything out left to right and has no RTL mode, so we carry a small patch to egui
0.36.2 in `vendor/egui` (used through `[patch.crates-io]` in the workspace `Cargo.toml`). Every
change is marked `Creative Studio`:

- `layout.rs`: a process-wide switch, `egui::set_rtl(bool)` / `egui::is_rtl()`, and
  `egui::start_align()` (left, or right when RTL). `Layout::default()` starts from it.
- `containers/panel.rs`: panels start from `Layout::default()`.
- `containers/menu.rs`, `containers/popup.rs`: menu bars run right to left, menus and popups align
  right.
- `ui.rs`: `ui.vertical` aligns to the start edge, and `ui.columns` puts the first column on the
  right. `ui.horizontal` already followed its parent's direction.
- `grid.rs`: grid columns run from the right.
- `widgets/checkbox.rs`, `widgets/radio_button.rs`: the box sits on the right of its label.

In our code (applied by `studio/rebrand.py`, so upstream merges keep it):
- `i18n.rs`: `is_rtl()` (the languages in `RTL_CODES`, now Arabic).
- `lib.rs`: turns the switch on each frame from `is_rtl()`, and puts the layers rail and the two
  side panels on the mirrored side. The panel edges (the drags that resize them) follow the panels.
- Names with Arabic letters are shown in visual order by `bidi.rs` (see its module comment).

## Upgrading egui

When upstream moves to a newer egui, the patch stops applying (Cargo warns that the patch is
unused, and `egui::set_rtl` no longer exists, so the build fails). Copy the new egui into
`vendor/egui` and re-apply the `Creative Studio` changes listed above.

## Still left to right

Widgets drawn at fixed coordinates: the canvas rulers, the document tabs, the layer rows' indent
and drag handles, the panel footer buttons, and dialogs laid out with fixed positions. They need
mirroring one by one.
