use tauri_plugin_sql::{Migration, MigrationKind};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let migrations = vec![
        Migration {
            version: 1,
            description: "create tax_returns and extracted_fields tables",
            sql: "
                CREATE TABLE IF NOT EXISTS tax_returns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tax_year INTEGER NOT NULL,
                    filing_status TEXT,
                    pdf_path TEXT NOT NULL,
                    pdf_filename TEXT NOT NULL,
                    extraction_method TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE(tax_year)
                );

                CREATE TABLE IF NOT EXISTS extracted_fields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    return_id INTEGER NOT NULL,
                    field_key TEXT NOT NULL,
                    field_label TEXT NOT NULL,
                    field_value TEXT,
                    field_type TEXT NOT NULL DEFAULT 'number',
                    category TEXT NOT NULL,
                    line_number TEXT,
                    confidence REAL DEFAULT 1.0,
                    needs_review INTEGER DEFAULT 0,
                    FOREIGN KEY (return_id) REFERENCES tax_returns(id) ON DELETE CASCADE,
                    UNIQUE(return_id, field_key)
                );

                CREATE INDEX IF NOT EXISTS idx_fields_return_id ON extracted_fields(return_id);
                CREATE INDEX IF NOT EXISTS idx_fields_category ON extracted_fields(category);
            ",
            kind: MigrationKind::Up,
        },
    ];

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations("sqlite:taxvisualizer.db", migrations)
                .build(),
        )
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
