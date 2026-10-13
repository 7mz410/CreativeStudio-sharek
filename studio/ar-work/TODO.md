# Arabic catalog: work left

Done (crates/ui-egui/locales/ar.toml, a draft): the File, Edit, View, Object, Text, Vector, Arrange
and Help menu headings, the core tools (move, frame, shapes, pen, text, hand, comment, section), the
core commands (file, edit, select, object, arrange, shapes, text basics, preferences, help), the
Boolean and select submenu items, the theme names, the About text, and the app name (sharek = شارك).

Left in English, to translate next (the shipped catalogs have about 2000 keys each):
- Dialogs and their buttons (Preferences, Export, Share, Version history, Libraries, Plugins).
- Status-bar and tooltip text, error messages, the Command Reference, and the rest of the commands.
- Plural rows (`{ one, other }`): none in ar.toml yet, so the plural rule is still the English one.
- Layout is still left to right. Arabic names and text display in visual order (see
  crates/ui-egui/src/bidi.rs), but panels, menus and toolbars do not mirror.
- Right-to-left layout for the whole interface (mirroring panels and the canvas rulers).
