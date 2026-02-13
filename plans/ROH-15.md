# Plan: Encryption at rest for local tax data (SQLCipher)

**Issue:** [ROH-15](https://linear.app/rohanr/issue/ROH-15/encryption-at-rest-for-local-tax-data-sqlcipher)
**Priority:** Low
**Status:** Planning

---

## Context

User tax data is currently stored in an unencrypted SQLite database on their local machine. While the data never leaves their computer, an unencrypted database means anyone with file access (malware, physical access, backup exposure) could read sensitive financial information.

**Why this matters:** Tax returns contain SSNs, income details, and financial data. The CLAUDE.md privacy principles explicitly require "Encryption at rest: Local SQLite database encrypted on disk."

**Why now:** This is Phase 3 of the enhanced data access work. Before we add more detailed/sensitive data (ROH-14, ROH-16), we should encrypt the storage layer.

## Summary

Replace the standard SQLite database with SQLCipher (AES-256 encrypted SQLite). Generate an encryption key on first launch, store it securely in the OS keychain via Tauri, and migrate existing unencrypted databases transparently.

## Technical Approach

### Why This Approach

SQLCipher is the industry standard for SQLite encryption. It's:
- **Transparent:** Same SQL API, just encrypted on disk
- **Battle-tested:** Used by Signal, 1Password, and many security-focused apps
- **Tauri-compatible:** `tauri-plugin-sql` supports SQLCipher via a feature flag

Think of it like putting your filing cabinet in a safe — the files inside work the same way, but now they're protected.

### Alternatives Considered

| Approach | Pros | Cons | Why Not |
|----------|------|------|---------|
| **Application-level encryption** | No SQLCipher dependency | Complex, error-prone, must encrypt each field | Reinventing the wheel poorly |
| **Full-disk encryption only** | No code changes | Not all users enable it, we can't verify | Can't rely on user configuration |
| **Encrypt just sensitive fields** | Smaller attack surface | Complex key management per field, breaks queries | SQLCipher handles this better |

SQLCipher provides full-database encryption with minimal code changes.

### Key Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Machine                            │
│  ┌──────────────────┐    ┌──────────────────────────────┐  │
│  │  OS Keychain     │    │  SQLCipher Database          │  │
│  │  ─────────────   │    │  ─────────────────────────   │  │
│  │  Encryption Key  │───▶│  AES-256 Encrypted Data     │  │
│  │  (protected by   │    │  (unreadable without key)   │  │
│  │   OS login)      │    │                              │  │
│  └──────────────────┘    └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

The encryption key is stored in the OS keychain (macOS Keychain / Windows Credential Manager), protected by the user's login credentials. The key never leaves the local machine.

## Task List

- 🔴 **Enable SQLCipher in Tauri** — Add feature flag
  - 🔴 Update Cargo.toml with `sqlcipher` feature
  - 🔴 Verify SQLCipher builds correctly
- 🔴 **Implement key management** — Generate and store encryption key
  - 🔴 Add tauri-plugin-keyring dependency
  - 🔴 Create Rust function to get-or-generate encryption key
  - 🔴 Store key in OS keychain on first launch
- 🔴 **Update database initialization** — Use encrypted connection
  - 🔴 Modify lib.rs to pass encryption key to SQLite
  - 🔴 Test encrypted database creation
- 🔴 **Implement migration** — Handle existing unencrypted databases
  - 🔴 Detect if existing database is unencrypted
  - 🔴 Export data, create encrypted DB, import data
  - 🔴 Delete unencrypted database after successful migration
- 🔴 **Add tests** — Verify encryption works
  - 🔴 Test key generation and retrieval
  - 🔴 Test database encryption
  - 🔴 Test migration from unencrypted
- 🔴 **Update documentation** — Note encryption in README/CLAUDE.md

**Legend:** 🔴 Not Started | 🟡 In Progress | 🟢 Complete

## Major Changes

### Cargo.toml — Enable SQLCipher

**Current state:**
```toml
tauri-plugin-sql = { version = "2", features = ["sqlite"] }
```

**After this change:**
```toml
tauri-plugin-sql = { version = "2", features = ["sqlite", "sqlcipher"] }
tauri-plugin-keyring = "0.1"  # For secure key storage
```

**Why:** The `sqlcipher` feature replaces standard SQLite with the encrypted variant.

### lib.rs — Encrypted Database Initialization

**Current state:**
```rust
tauri_plugin_sql::Builder::default()
    .add_migrations("sqlite:taxvisualizer.db", migrations)
    .build()
```

**After this change:**
```rust
// Get or generate encryption key
let key = get_or_create_encryption_key()?;

tauri_plugin_sql::Builder::default()
    .add_migrations(
        &format!("sqlite:taxvisualizer.db?key={}", key),
        migrations
    )
    .build()
```

**Why:** SQLCipher uses a key parameter in the connection string to encrypt/decrypt.

### New Rust Module — Key Management

```rust
// src/keyring.rs
use tauri_plugin_keyring::Keyring;

const SERVICE_NAME: &str = "com.taxvisualizer.app";
const KEY_NAME: &str = "database-encryption-key";

pub fn get_or_create_encryption_key() -> Result<String, Error> {
    let keyring = Keyring::new(SERVICE_NAME, KEY_NAME)?;

    // Try to get existing key
    match keyring.get_password() {
        Ok(key) => Ok(key),
        Err(_) => {
            // Generate new key (32 bytes = 256 bits)
            let key = generate_secure_key();
            keyring.set_password(&key)?;
            Ok(key)
        }
    }
}

fn generate_secure_key() -> String {
    use rand::Rng;
    let mut rng = rand::thread_rng();
    let bytes: [u8; 32] = rng.gen();
    hex::encode(bytes)  // 64-char hex string
}
```

## Implementation Details

### Migration Flow for Existing Users

```
App launches
    ↓
Check: Does taxvisualizer.db exist?
    ↓
Yes → Is it encrypted? (try opening with key)
    ↓
No, it's unencrypted → Run migration:
    1. Open unencrypted DB
    2. Create new encrypted DB (temp name)
    3. Copy all tables: tax_returns, extracted_fields
    4. Verify row counts match
    5. Delete unencrypted DB
    6. Rename encrypted DB to taxvisualizer.db
    ↓
Continue with encrypted database
```

### Detecting Unencrypted Database

```rust
fn is_database_encrypted(path: &str, key: &str) -> bool {
    // Try to open with encryption key
    // If it fails with "not a database" error, it's unencrypted
    match Database::open(&format!("{}?key={}", path, key)) {
        Ok(_) => true,   // Successfully opened as encrypted
        Err(e) if e.contains("not a database") => false,  // Unencrypted
        Err(_) => true,  // Other error, assume encrypted with wrong key
    }
}
```

### Data Flow

```
First Launch:
    1. Generate 256-bit encryption key
    2. Store in OS keychain
    3. Create encrypted database
    4. Run migrations

Subsequent Launches:
    1. Retrieve key from OS keychain
    2. Open encrypted database
    3. Normal operation (encryption transparent)

Existing User Upgrade:
    1. Retrieve key from OS keychain (or generate if new)
    2. Detect unencrypted database
    3. Migrate data to encrypted database
    4. Continue normally
```

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| Modify | `app/src-tauri/Cargo.toml` | Add sqlcipher feature, keyring dependency |
| Create | `app/src-tauri/src/keyring.rs` | Key generation and storage |
| Modify | `app/src-tauri/src/lib.rs` | Use encrypted database connection |
| Create | `app/src-tauri/src/migration.rs` | Unencrypted → encrypted migration |

## Testing Strategy

### What to Test
- **Key generation** — Verify 256-bit key is generated
- **Key persistence** — Verify key survives app restart
- **Encryption verification** — Verify raw database file is unreadable
- **Migration** — Verify existing data survives migration
- **Normal operation** — Verify all CRUD operations still work

### How to Verify
1. Build and run app
2. Upload a tax return
3. Close app
4. Try to open `taxvisualizer.db` with standard SQLite tools → should fail
5. Reopen app → data should be intact
6. Query keychain to verify key exists

```bash
# macOS: Check keychain
security find-generic-password -s "com.taxvisualizer.app" -a "database-encryption-key"

# Windows: Check Credential Manager (via GUI or cmdkey)
```

## Risks & Considerations

- **Key loss:**
  - *Impact:* If keychain is cleared, data is unrecoverable
  - *Mitigation:* Document this clearly. Consider optional key backup/export feature.

- **Build complexity:**
  - *Impact:* SQLCipher requires OpenSSL or similar crypto library
  - *Mitigation:* Use bundled/vendored crypto in tauri-plugin-sql. Test on both platforms.

- **Performance:**
  - *Impact:* Encryption adds ~5-15% overhead to database operations
  - *Mitigation:* Acceptable for this use case. Profile if issues arise.

- **Migration failures:**
  - *Impact:* Could lose user data during upgrade
  - *Mitigation:* Keep backup of original DB until migration verified. Atomic rename.

## Performance Implications

SQLCipher adds approximately 5-15% overhead to database operations. For our use case (small dataset, infrequent writes), this is negligible. Read/write times will remain under 10ms.

## Dependencies

- **tauri-plugin-keyring** — For OS keychain access
- **rand** — For secure key generation
- **hex** — For key encoding

## Open Questions

1. **Key backup:** Should we provide a way for users to export/backup their encryption key?
   - Pro: Recovery option if keychain is lost
   - Con: Increases attack surface, user responsibility
   - *Recommendation:* Defer to future version. Document risk clearly.

---

*This plan was created by your CTO assistant. Review the approach and ask questions before we proceed to implementation.*
