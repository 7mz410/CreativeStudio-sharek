# Arabic interface: work left

Done:
- Catalog: `crates/ui-egui/locales/ar.toml` has every interface string (1545), every command label
  (556) and the main-menu labels that differ from their commands (31). It is a draft, marked
  `draft — needs native review` in `[meta]`. Keep `{placeholders}` as English has them.
- Right-to-left layout (studio/RTL.md): the layers rail and the Layers panel move to the right, the
  Design panel to the left, and menus and rows run from the right. The egui patch is in
  `vendor/egui` (the same egui 0.36.2 as rsm).
- Arabic names display in visual order (`crates/ui-egui/src/bidi.rs`).

Left:
- Native review of the whole catalog (the draft is machine-assisted; terms such as "مثيل" for
  instance and "نسخة بديلة" for variant are choices to confirm).
- Plural rows have `one` and `other` only: Arabic has six CLDR plural forms (zero, one, two, few,
  many, other) and the lookup supports two. Counts 2, and 3 to 10 read the `other` form.
- Still left to right: the canvas rulers, the document tabs, the layer rows' indent and drag
  handles, the panel footer buttons and some dialogs laid out at fixed positions.
- The Arabic font comes from storytold/craft-fonts (`CRAFT_FONTS_DIR`, Noto Sans Arabic). A build
  without it falls back to the system's Arabic fonts.
