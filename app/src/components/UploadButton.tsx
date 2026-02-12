import { open } from "@tauri-apps/plugin-dialog";

interface UploadButtonProps {
  onFileSelected: (path: string, filename: string) => void;
}

export function UploadButton({ onFileSelected }: UploadButtonProps) {
  const handleClick = async () => {
    const selected = await open({
      multiple: false,
      filters: [{ name: "PDF", extensions: ["pdf"] }],
    });

    if (selected) {
      const path = typeof selected === "string" ? selected : selected;
      const filename = path.split(/[\\/]/).pop() ?? "unknown.pdf";
      onFileSelected(path, filename);
    }
  };

  return (
    <button className="upload-btn" onClick={handleClick}>
      + Upload Tax Return
    </button>
  );
}
