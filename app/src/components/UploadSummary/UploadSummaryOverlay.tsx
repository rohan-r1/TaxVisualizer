export interface FormFieldCount {
  form: string;
  count: number;
}

export interface UploadSummaryProps {
  year: number;
  filingStatus: string;
  formFieldCounts: FormFieldCount[];
  onContinue: () => void;
  onReUpload: () => void;
}

export function UploadSummaryOverlay({
  year,
  filingStatus,
  formFieldCounts,
  onContinue,
  onReUpload,
}: UploadSummaryProps) {
  return (
    <div className="upload-summary-overlay" onClick={onReUpload}>
      <div
        className="upload-summary-panel"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="upload-summary-header">
          <h3>Upload Summary</h3>
          <span className="upload-summary-year">{year}</span>
        </div>

        <div className="upload-summary-content">
          <ul className="detected-forms-list">
            {formFieldCounts.map(({ form, count }) => (
              <li key={form} className="detected-form-item">
                <svg
                  className="check-icon"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span className="form-name">{form}</span>
                <span className="form-field-count">{count} fields</span>
              </li>
            ))}
          </ul>

          <p className="upload-summary-status">
            <span className="status-label">Filing Status:</span> {filingStatus}
          </p>
        </div>

        <div className="upload-summary-actions">
          <button className="upload-summary-btn-secondary" onClick={onReUpload}>
            Re-upload
          </button>
          <button className="upload-summary-btn-primary" onClick={onContinue}>
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
