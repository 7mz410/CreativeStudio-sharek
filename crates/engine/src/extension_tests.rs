//! Documents save as `.sharek` by default, and a `.figcraft` file still opens.

use serde_json::json;

use crate::Session;

#[test]
fn save_as_without_extension_writes_sharek_and_figcraft_still_opens() {
    let dir = std::env::temp_dir().join(format!("sharek-extension-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let mut s = Session::new();
    s.execute("shape.rectangle", &json!({"name": "box", "x": 1, "y": 2, "width": 3, "height": 4})).unwrap();
    s.execute("file.saveAs", &json!({"path": dir.join("doc").to_string_lossy()})).unwrap();
    let saved = dir.join("doc.sharek");
    assert!(saved.exists(), "saved as .sharek");
    // The same contents under upstream's extension open as before.
    let old = dir.join("old.figcraft");
    std::fs::copy(&saved, &old).unwrap();
    let mut t = Session::new();
    t.execute("file.open", &json!({"path": old.to_string_lossy()})).unwrap();
    assert_eq!(t.ds().unwrap().path.as_deref(), Some(old.to_string_lossy().as_ref()));
    let _ = std::fs::remove_dir_all(&dir);
}
