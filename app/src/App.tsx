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
import type { TaxReturn, ExtractedField, ReturnSummary } from "./types/tax";
import "./App.css";

function App() {
  const [returns, setReturns] = useState<TaxReturn[]>([]);
  const [fields, setFields] = useState<Record<number, ExtractedField[]>>({});
  const [summaries, setSummaries] = useState<ReturnSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

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
  }, [loadData]);

  const handleFileSelected = async (path: string, filename: string) => {
    try {
      setError(null);

      // Extract data (mock for now, will be replaced by real pipeline)
      const extracted = mockExtract(filename);

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

  return (
    <div className="app">
      <header className="app-header">
        <h1>TaxVisualizer</h1>
        <div className="app-header-actions">
          <UploadButton onFileSelected={handleFileSelected} />
        </div>
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
          </aside>
          <div className="app-content-wrapper">
            <section className="app-content">
              <Dashboard
                returns={returns}
                fields={fields}
                summaries={summaries}
              />
            </section>
            {/* Chatbot panel - always visible, expands on focus */}
            <ChatbotPanel
              returns={returns}
              fields={fields}
              summaries={summaries}
              onOpenSettings={() => setSettingsOpen(true)}
            />
          </div>
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
