import { useState } from "react";
import type { ValidationResult, ValidationIssue } from "../../services/extractionValidator";

export interface FormFieldCount {
  form: string;
  count: number;
}

export interface UploadSummaryProps {
  year: number;
  filingStatus: string;
  formFieldCounts: FormFieldCount[];
  validationResult?: ValidationResult;
  onContinue: () => void;
  onReUpload: () => void;
}

/** Get the overall validation status for display */
function getValidationStatus(result: ValidationResult | undefined): {
  status: "passed" | "warnings" | "errors";
  label: string;
  count: number;
} {
  if (!result || result.issues.length === 0) {
    return { status: "passed", label: "Validation Passed", count: 0 };
  }

  const errorCount = result.issues.filter((i) => i.severity === "error").length;
  const warningCount = result.issues.filter((i) => i.severity === "warning").length;

  if (errorCount > 0) {
    return {
      status: "errors",
      label: `Validation Errors (${errorCount})`,
      count: errorCount,
    };
  }

  return {
    status: "warnings",
    label: `Validation Warnings (${warningCount})`,
    count: warningCount,
  };
}

/** Render a single validation issue */
function ValidationIssueItem({ issue }: { issue: ValidationIssue }) {
  return (
    <li className={`validation-issue validation-issue-${issue.severity}`}>
      <div className="validation-issue-header">
        <span className="validation-issue-icon">
          {issue.severity === "error" ? (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="15" y1="9" x2="9" y2="15" />
              <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          )}
        </span>
        <span className="validation-issue-field">{issue.field}</span>
      </div>
      <p className="validation-issue-message">{issue.message}</p>
      {issue.expected && issue.actual && (
        <p className="validation-issue-detail">
          Expected {issue.expected}, got {issue.actual}
        </p>
      )}
    </li>
  );
}

export function UploadSummaryOverlay({
  year,
  filingStatus,
  formFieldCounts,
  validationResult,
  onContinue,
  onReUpload,
}: UploadSummaryProps) {
  const [issuesExpanded, setIssuesExpanded] = useState(true);
  const validationStatus = getValidationStatus(validationResult);
  const hasIssues = validationResult && validationResult.issues.length > 0;

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

          {/* Validation status section */}
          <div className={`validation-status validation-status-${validationStatus.status}`}>
            <button
              className="validation-status-header"
              onClick={() => hasIssues && setIssuesExpanded(!issuesExpanded)}
              disabled={!hasIssues}
            >
              <span className="validation-status-icon">
                {validationStatus.status === "passed" ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : validationStatus.status === "errors" ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                )}
              </span>
              <span className="validation-status-label">{validationStatus.label}</span>
              {hasIssues && (
                <span className={`validation-chevron ${issuesExpanded ? "expanded" : ""}`}>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </span>
              )}
            </button>

            {hasIssues && issuesExpanded && (
              <ul className="validation-issues-list">
                {validationResult.issues.map((issue, index) => (
                  <ValidationIssueItem key={`${issue.field}-${index}`} issue={issue} />
                ))}
              </ul>
            )}
          </div>
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
