# sharek: changes from upstream FigCraft

Required by the Apache License 2.0 (section 4b): files we changed carry this notice through
this list.

- Branding (user-visible only, applied by `studio/rebrand.py`): the app name sharek, the bundle id
  `ps.creative.studio.sharek`, links to sharek.studio.creative.ps and this repository. Crate names,
  settings folders and the file format keep their upstream names.
- No Discord buttons; community links point to Creative Studio.
- App icon: the sharek star on navy (`assets/app-icon/`).
- Removed upstream's ArtCraft brand assets (`docs/brand/`), as their brand terms require of forks.
- README (upstream's is `docs/UPSTREAM-README.md`) and NOTICE: the fork, its credits and the suite.
- Share ▸ Online: the built-in server is empty (`crates/engine/src/live.rs`, `DEFAULT_SERVER`), so files
  are not sent to collab.craftapps.dev (ArtCraft's public server) by default. Online sharing stays off
  until a server is entered in Preferences, or a build sets `FIGCRAFT_DEFAULT_SERVER`. Local-network
  sharing is unchanged.
- Arabic interface: `crates/ui-egui/locales/ar.toml` (every string; a draft that awaits a native
  speaker's review, see `studio/ar-work/TODO.md`), `studio/arabic_names.py` puts the Arabic name شارك in the Arabic catalogs,
  and the interface lays out right to left (`studio/RTL.md`, `vendor/egui`).
- The mark: the sharek star (`docs/studio/sharek.svg`, drawn by `crates/ui-egui/src/studio_mark.rs`, generated
  by `studio/rebrand.py`) replaces the upstream chameleon tail in the logo icon and the About tile.
  English, see `studio/ar-work/TODO.md`). `studio/arabic_names.py` puts the Arabic name شارك in the Arabic catalogs.
- Loading screen of the web version: the app's star (`studio/` splash, `apps/figcraft-web/index.html`).
