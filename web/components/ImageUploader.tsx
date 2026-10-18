export default function ImageUploader({
  onFile,
}: {
  onFile: (file: File) => void;
}) {
  return (
    <label className="upload">
      Open microscopy image
      <input
        aria-label="Upload microscopy image"
        type="file"
        accept=".png,.jpg,.jpeg,.tif,.tiff"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
        }}
      />
      <small>PNG · JPEG · TIFF / single frame</small>
    </label>
  );
}
