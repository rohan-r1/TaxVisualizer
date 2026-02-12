import type { TaxReturn } from "../types/tax";

interface ReturnsListProps {
  returns: TaxReturn[];
  onDelete: (id: number) => void;
}

export function ReturnsList({ returns, onDelete }: ReturnsListProps) {
  if (returns.length === 0) return null;

  return (
    <div className="returns-list">
      <h3>Uploaded Returns</h3>
      <ul>
        {returns.map((r) => (
          <li key={r.id} className="return-item">
            <span className="return-year">{r.tax_year}</span>
            <span className="return-filename">{r.pdf_filename}</span>
            <span className="return-status">
              {r.filing_status ?? "Processing..."}
            </span>
            <button
              className="delete-btn"
              onClick={() => onDelete(r.id)}
              title="Delete this return"
            >
              x
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
