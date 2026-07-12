use std::path::PathBuf;
use std::process::Command;

/// 从 exe 所在位置向上找含 backend/app.py 的应用根目录。
/// 兼容 exe 放仓库根(旁边有 backend/)或 target/release 深层目录。
fn find_app_root() -> Option<PathBuf> {
    let mut dir = std::env::current_exe().ok()?.parent()?.to_path_buf();
    for _ in 0..7 {
        if dir.join("backend").join("app.py").exists() {
            return Some(dir);
        }
        match dir.parent() {
            Some(p) => dir = p.to_path_buf(),
            None => break,
        }
    }
    None
}

/// 启动时拉起 Python 后端(uvicorn);后端在 127.0.0.1:8000 同时托管界面与 API。
fn spawn_backend() {
    if let Some(root) = find_app_root() {
        let _ = Command::new("python")
            .args(["-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"])
            .current_dir(root.join("backend"))
            .spawn();
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            spawn_backend();
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
