# Sidecar Pattern (and Why We're Using Python with Tauri)

**Date:** 2026-02-12
**Context:** ROH-17 planning — PDF extraction for TaxVisualizer
**Category:** Architecture

---

## The Quick Answer

A **sidecar** is a separate program that runs alongside your main application to handle specialized tasks. In our case, we're bundling a Python executable with our Tauri app because Python has better PDF parsing libraries (pdfplumber) than JavaScript. The main app spawns the Python process when needed, sends it a file path, and receives structured data back.

## The Full Explanation

### What It Is

Think of a sidecar like a motorcycle sidecar — it's attached to the main vehicle, travels with it, but has its own separate space and purpose. In software:

```
┌─────────────────────────────────────────┐
│           Your Main Application          │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │   Main Process  │  │   Sidecar     │ │
│  │   (Rust/TS)     │◄─►│   (Python)    │ │
│  │                 │  │               │ │
│  │  • UI logic     │  │  • PDF parsing│ │
│  │  • Database     │  │  • Specialized│ │
│  │  • User input   │  │    libraries  │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
```

The sidecar:
- **Ships with your app** — bundled in the installer
- **Runs as a separate process** — has its own memory, can crash independently
- **Communicates via simple protocols** — usually stdin/stdout with JSON

### Why It Exists

Different programming languages excel at different things:

| Language | Good At | Not Great At |
|----------|---------|--------------|
| **Rust** | Performance, safety, system access | Rapid prototyping, ML/data libraries |
| **TypeScript** | UI, async, web ecosystem | Heavy computation, system access |
| **Python** | Data science, PDF/ML libraries, scripting | Performance, bundling |

When your app needs capabilities from another language's ecosystem, you have three choices:

1. **Rewrite the library** in your language — expensive, error-prone
2. **Call an API** — adds latency, requires internet, privacy concerns
3. **Use a sidecar** — best of both worlds for desktop apps

### How It Works

Here's the flow for our PDF extraction:

```
User uploads PDF
       │
       ▼
┌──────────────────┐
│  TypeScript UI   │
│  "Extract this"  │
└────────┬─────────┘
         │ invoke Tauri command
         ▼
┌──────────────────┐
│  Rust Backend    │
│  spawn process   │────────────────┐
└────────┬─────────┘                │
         │                          │
         ▼                          ▼
┌──────────────────┐      ┌──────────────────┐
│  Python Sidecar  │      │  extract.exe     │
│  (pdfplumber)    │      │  (bundled)       │
│                  │      └──────────────────┘
│  1. Open PDF     │
│  2. Extract text │
│  3. Parse fields │
│  4. Return JSON  │
└────────┬─────────┘
         │ stdout: {"fields": [...]}
         ▼
┌──────────────────┐
│  Rust Backend    │
│  parse JSON      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  TypeScript UI   │
│  display results │
└──────────────────┘
```

**Key steps:**

1. **Bundling:** We use PyInstaller to compile the Python script + dependencies into a standalone executable. No Python installation needed on user's machine.

2. **Spawning:** Rust's `Command` API (or Tauri's sidecar helper) starts the process:
   ```rust
   Command::new_sidecar("extract")
       .args(["/path/to/tax_return.pdf"])
       .output()
   ```

3. **Communication:** The sidecar reads the file path from command-line args, does its work, and prints JSON to stdout. The parent process captures this output.

4. **Lifecycle:** The sidecar starts, does one job, and exits. No long-running process to manage.

### When You'll See This Again

Sidecars are common in:

- **Desktop apps** needing specialized libraries (ML, video processing, scientific computing)
- **Microservices** where a helper container runs alongside the main container (Kubernetes sidecar pattern)
- **Build tools** that need capabilities from multiple languages
- **Electron/Tauri apps** bridging web tech with system capabilities

## Code Example

**Python sidecar (extract.py):**
```python
#!/usr/bin/env python3
import sys
import json
import pdfplumber

def extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Extract text from specific coordinates
        page = pdf.pages[0]
        wages = page.crop((515, 158, 595, 172)).extract_text()

        return {
            "fields": [
                {"key": "wages", "value": wages}
            ]
        }

if __name__ == "__main__":
    pdf_path = sys.argv[1]           # Get path from command line
    result = extract(pdf_path)
    print(json.dumps(result))        # Output JSON to stdout
```

**Rust caller:**
```rust
#[tauri::command]
async fn extract_pdf(path: String) -> Result<Value, String> {
    // Spawn the bundled Python executable
    let output = Command::new_sidecar("extract")
        .map_err(|e| e.to_string())?
        .args([&path])
        .output()
        .await
        .map_err(|e| e.to_string())?;

    // Parse the JSON output
    let result: Value = serde_json::from_slice(&output.stdout)
        .map_err(|e| e.to_string())?;

    Ok(result)
}
```

**TypeScript caller:**
```typescript
// In React component
const result = await invoke("extract_pdf", { path: "/path/to/1040.pdf" });
console.log(result.fields);  // [{ key: "wages", value: "75000" }]
```

## Related Concepts

- **IPC (Inter-Process Communication)** — How separate processes talk to each other (stdin/stdout, sockets, pipes)
- **PyInstaller** — Tool that bundles Python scripts into standalone executables
- **Tauri Sidecar** — Tauri's built-in support for bundling and spawning external executables
- **Microservices Sidecar** — Similar pattern in cloud architecture (e.g., Envoy proxy)
- **FFI (Foreign Function Interface)** — Alternative approach: calling other languages directly (more complex)

## Key Takeaway

A sidecar lets you use the best tool for each job — in our case, Python's excellent PDF libraries — without rewriting everything or requiring users to install Python. It's like hiring a specialist contractor: they show up, do their specific job, and leave.

---

*Learning note from your CTO assistant*
