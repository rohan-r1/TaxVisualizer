import { useState, useEffect, useCallback } from "react";
import { UploadButton } from "./components/UploadButton";
import { ReturnsList } from "./components/ReturnsList";
import { Dashboard } from "./components/Dashboard";
import { ChatbotPanel } from "./components/Chatbot";
import { SettingsPanel } from "./components/Settings";
import {
  getAllReturns,
  getAllFields,
  insertReturn,
  insertFieldsBatch,
  deleteReturn,
  buildSummary,
} from "./db/database";
import { mockExtract } from "./db/mockExtraction";
import { extractPdf, checkSidecarAvailable } from "./services/pdfExtractor";
import type { TaxReturn, ExtractedField, ReturnSummary } from "./types/tax";
import "./App.css";

function App() {
  const [returns, setReturns] = useState<TaxReturn[]>([]);
  const [fields, setFields] = useState<Record<number, ExtractedField[]>>({});
  const [summaries, setSummaries] = useState<ReturnSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [sidecarAvailable, setSidecarAvailable] = useState<boolean | null>(null);

  const loadData = useCallback(async () => {
    try {
      const allReturns = await getAllReturns();
      const allFields = await getAllFields();
      setReturns(allReturns);
      setFields(allFields);

      const sums = allReturns.map((r) =>
        buildSummary(r, allFields[r.id] ?? [])
      );
      setSummaries(sums);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Check if the Python sidecar is available
    checkSidecarAvailable().then(setSidecarAvailable);
  }, [loadData]);

  const handleFileSelected = async (path: string, filename: string) => {
    try {
      setError(null);
      setExtracting(true);

      let extracted;

      // Try real PDF extraction if sidecar is available
      if (sidecarAvailable) {
        console.log("Using Python sidecar for PDF extraction");
        const result = await extractPdf(path);

        if (result.error) {
          // Sidecar extraction failed, fall back to mock
          console.warn("Sidecar extraction failed:", result.error);
          console.log("Falling back to mock extraction");
          extracted = mockExtract(filename);
        } else {
          // Convert sidecar result to our format
          // Note: insertFieldsBatch expects key/label/value, not fieldKey/fieldLabel/fieldValue
          extracted = {
            year: result.year,
            filingStatus: result.filing_status,
            extractionMethod: result.extraction_method,
            fields: result.fields.map((f) => ({
              key: f.key,
              label: f.label,
              value: f.value,
              fieldType: "number" as const,
              category: f.category,
              lineNumber: f.line_number,
              confidence: f.confidence,
            })),
          };
        }
      } else {
        // Sidecar not available, use mock extraction
        console.log("Sidecar not available, using mock extraction");
        extracted = mockExtract(filename);
      }

      // Store in database
      const returnId = await insertReturn(
        extracted.year,
        path,
        filename,
        extracted.filingStatus,
        extracted.extractionMethod
      );
      await insertFieldsBatch(returnId, extracted.fields);

      // Refresh UI
      await loadData();
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("UNIQUE constraint")) {
        setError(
          `A return for that year already exists. Delete it first to re-upload.`
        );
      } else {
        setError(msg);
      }
    } finally {
      setExtracting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setError(null);
      await deleteReturn(id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  if (loading) {
    return <div className="app-loading">Loading...</div>;
  }

  if (extracting) {
    return (
      <div className="app-loading">
        <span>Extracting PDF...</span>
        <span className="loading-subtext">
          Analyzing form fields with pdfplumber
        </span>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>TaxVisualizer</h1>
      </header>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>dismiss</button>
        </div>
      )}

      <div className="app-body">
        <main className="app-main">
          <aside className="app-sidebar">
            <ReturnsList returns={returns} onDelete={handleDelete} />
            <UploadButton onFileSelected={handleFileSelected} />
          </aside>
          {/* Chatbot panel - full-height left column */}
          <ChatbotPanel
            returns={returns}
            fields={fields}
            summaries={summaries}
            onOpenSettings={() => setSettingsOpen(true)}
          />
          <section className="app-content">
            <Dashboard
              returns={returns}
              fields={fields}
              summaries={summaries}
            />
          </section>
        </main>
      </div>

      {/* Settings panel */}
      {settingsOpen && (
        <SettingsPanel onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  );
}

export default App;
