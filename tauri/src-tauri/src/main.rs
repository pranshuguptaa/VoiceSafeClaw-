#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager,
};

#[derive(Clone, serde::Serialize)]
struct StatusPayload {
    status: String,
    listening: bool,
}

#[tauri::command]
fn get_engine_status() -> StatusPayload {
    StatusPayload {
        status: "running".into(),
        listening: true,
    }
}

#[tauri::command]
fn set_wake_word(word: String) -> Result<String, String> {
    // Forward to Python sidecar via env or IPC
    std::env::set_var("WAKE_WORD", &word);
    Ok(format!("Wake word set to: {}", word))
}

#[tauri::command]
fn set_tts_engine(engine: String) -> Result<String, String> {
    std::env::set_var("TTS_ENGINE", &engine);
    Ok(format!("TTS engine set to: {}", engine))
}

#[tauri::command]
fn set_sandbox_mode(enabled: bool) -> Result<String, String> {
    std::env::set_var("SANDBOX_MODE", if enabled { "true" } else { "false" });
    Ok(format!("Sandbox mode: {}", enabled))
}

#[tauri::command]
fn approve_action(action_id: String, approved: bool) -> Result<String, String> {
    Ok(format!(
        "Action {} {}",
        action_id,
        if approved { "approved" } else { "rejected" }
    ))
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            // Build tray menu
            let show = MenuItem::with_id(app, "show", "Settings", true, None::<&str>)?;
            let status = MenuItem::with_id(app, "status", "✅ Listening", false, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit VoiceSafeClaw", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&status, &show, &quit])?;

            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .tooltip("VoiceSafeClaw — Listening")
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "show" => {
                        if let Some(w) = app.get_webview_window("main") {
                            let _ = w.show();
                            let _ = w.set_focus();
                        }
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(w) = app.get_webview_window("main") {
                            let _ = w.show();
                            let _ = w.set_focus();
                        }
                    }
                })
                .build(app)?;

            // Spawn Python sidecar
            #[cfg(not(debug_assertions))]
            {
                use tauri_plugin_shell::ShellExt;
                let sidecar = app.shell().sidecar("voicesafeclaw-engine").unwrap();
                let (_rx, _child) = sidecar.spawn().expect("Failed to start engine sidecar");
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_engine_status,
            set_wake_word,
            set_tts_engine,
            set_sandbox_mode,
            approve_action,
        ])
        .run(tauri::generate_context!())
        .expect("error while running VoiceSafeClaw");
}
