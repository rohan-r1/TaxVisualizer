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
import { extractPdf, checkSidecarAvailable } from "./services/pdfExtractor";
import type { TaxReturn, ExtractedField, ReturnSummary } from "./types/tax";
import type { ChartConfig } from "./types/chart";
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
  const [customCharts, setCustomCharts] = useState<ChartConfig[]>([]);
  const [hiddenWidgets, setHiddenWidgets] = useState<string[]>([]);

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

      // Require sidecar for PDF extraction
      if (!sidecarAvailable) {
        throw new Error(
          "PDF extraction unavailable. Please build the Python sidecar: cd app/src-tauri/python && python build.py"
        );
      }

      console.log("Using Python sidecar for PDF extraction");
      const result = await extractPdf(path);

      if (result.error) {
        throw new Error(`PDF extraction failed: ${result.error}`);
      }

      // Convert sidecar result to our format
      const extracted = {
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

  const handleCreateChart = useCallback((config: ChartConfig) => {
    setCustomCharts((prev) => [config, ...prev]); // Add to front (top)
  }, []);

  const handleRemoveChart = useCallback((id: string) => {
    setCustomCharts((prev) => prev.filter((c) => c.id !== id));
  }, []);

  const handleHideWidget = useCallback((id: string) => {
    setHiddenWidgets((prev) => [...prev, id]);
  }, []);

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
            <UploadButton onFileSelected={handleFileSelected} />
            <ReturnsList returns={returns} onDelete={handleDelete} />
          </aside>
          {/* Chatbot panel - full-height left column */}
          <ChatbotPanel
            returns={returns}
            fields={fields}
            summaries={summaries}
            onOpenSettings={() => setSettingsOpen(true)}
            onCreateChart={handleCreateChart}
          />
          <section className="app-content">
            <Dashboard
              returns={returns}
              fields={fields}
              summaries={summaries}
              customCharts={customCharts}
              onRemoveChart={handleRemoveChart}
              onRemoveWidget={handleHideWidget}
              hiddenWidgets={hiddenWidgets}
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
