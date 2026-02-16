import { useState, useEffect, useCallback } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { UploadButton } from "./components/UploadButton";
import { ReturnsList } from "./components/ReturnsList";
import { Dashboard } from "./components/Dashboard";
import { ChatbotPanel } from "./components/Chatbot";
import { SettingsPanel } from "./components/Settings";
import {
  UploadSummaryOverlay,
  type FormFieldCount,
} from "./components/UploadSummary";
import {
  getAllReturns,
  getAllFields,
  insertReturn,
  insertFieldsBatch,
  deleteReturn,
  buildSummary,
} from "./db/database";
import {
  extractPdf,
  checkSidecarAvailable,
  type ExtractionResult,
  type ExtractionProgress,
} from "./services/pdfExtractor";
import {
  validateExtraction,
  type ValidationResult,
} from "./services/extractionValidator";
import type { TaxReturn, ExtractedField, ReturnSummary } from "./types/tax";
import type { ChartConfig } from "./types/chart";
import "./App.css";

/** Pending upload awaiting user confirmation */
interface PendingUpload {
  path: string;
  filename: string;
  result: ExtractionResult;
  validationResult: ValidationResult;
}

/** Build field counts per detected form for the upload summary */
function buildFormFieldCounts(result: ExtractionResult): FormFieldCount[] {
  const detectedForms = result.detected_forms || ["Form 1040"];
  const fields = result.fields;

  // Map category prefixes to form names
  const categoryToForm: Record<string, string> = {
    schedule_1: "Schedule 1",
    schedule_2: "Schedule 2",
    schedule_a: "Schedule A",
    schedule_c: "Schedule C",
  };

  // Count fields per form
  const counts: Record<string, number> = {};
  for (const form of detectedForms) {
    counts[form] = 0;
  }

  for (const field of fields) {
    const formName = categoryToForm[field.category];
    if (formName && counts[formName] !== undefined) {
      counts[formName]++;
    } else {
      // Default to Form 1040 for non-schedule categories
      counts["Form 1040"] = (counts["Form 1040"] || 0) + 1;
    }
  }

  // Convert to array, keeping detected order
  return detectedForms.map((form) => ({
    form,
    count: counts[form] || 0,
  }));
}

function App() {
  const [returns, setReturns] = useState<TaxReturn[]>([]);
  const [fields, setFields] = useState<Record<number, ExtractedField[]>>({});
  const [summaries, setSummaries] = useState<ReturnSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [extractionProgress, setExtractionProgress] =
    useState<ExtractionProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [sidecarAvailable, setSidecarAvailable] = useState<boolean | null>(null);
  const [customCharts, setCustomCharts] = useState<ChartConfig[]>([]);
  const [hiddenWidgets, setHiddenWidgets] = useState<string[]>([]);
  const [pendingUpload, setPendingUpload] = useState<PendingUpload | null>(null);

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
      setExtractionProgress(null);

      // Require sidecar for PDF extraction
      if (!sidecarAvailable) {
        throw new Error(
          "PDF extraction unavailable. Please build the Python sidecar: cd app/src-tauri/python && python build.py"
        );
      }

      console.log("Using Python sidecar for PDF extraction");
      const result = await extractPdf(path, (progress) => {
        setExtractionProgress(progress);
      });

      if (result.error) {
        throw new Error(`PDF extraction failed: ${result.error}`);
      }

      // Run validation on extracted data
      const validationResult = validateExtraction(result);

      // Apply confidence updates to fields if validation found issues
      if (validationResult.fieldUpdates.size > 0) {
        result.fields = result.fields.map((f) => ({
          ...f,
          confidence:
            validationResult.fieldUpdates.get(f.key) ?? f.confidence,
        }));
      }

      // Show upload summary overlay for user confirmation
      setPendingUpload({ path, filename, result, validationResult });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setExtracting(false);
      setExtractionProgress(null);
    }
  };

  const handleConfirmUpload = async () => {
    if (!pendingUpload) return;

    const { path, filename, result } = pendingUpload;

    try {
      setError(null);

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

      // Clear pending upload and refresh UI
      setPendingUpload(null);
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
      // Keep pending upload open so user can re-upload if desired
    }
  };

  const handleCancelUpload = async () => {
    setPendingUpload(null);

    // Open file dialog directly to save the user a click
    const selected = await open({
      multiple: false,
      filters: [{ name: "PDF", extensions: ["pdf"] }],
    });

    if (selected) {
      const path = typeof selected === "string" ? selected : selected;
      const filename = path.split(/[\\/]/).pop() ?? "unknown.pdf";
      handleFileSelected(path, filename);
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
          {extractionProgress?.message || "Initializing OCR..."}
        </span>
        {extractionProgress?.current !== undefined &&
          extractionProgress?.total !== undefined && (
            <div className="extraction-progress">
              <div
                className="extraction-progress-bar"
                style={{
                  width: `${(extractionProgress.current / extractionProgress.total) * 100}%`,
                }}
              />
            </div>
          )}
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

      {/* Upload summary overlay */}
      {pendingUpload && (
        <UploadSummaryOverlay
          year={pendingUpload.result.year}
          filingStatus={pendingUpload.result.filing_status}
          formFieldCounts={buildFormFieldCounts(pendingUpload.result)}
          validationResult={pendingUpload.validationResult}
          onContinue={handleConfirmUpload}
          onReUpload={handleCancelUpload}
        />
      )}
    </div>
  );
}

export default App;
