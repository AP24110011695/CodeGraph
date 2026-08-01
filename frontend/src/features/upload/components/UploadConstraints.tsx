export function UploadConstraints() {
  return (
    <ul className="space-y-1 text-xs text-text-tertiary">
      <li>Supported format: .zip archives only</li>
      <li>Recommended size: 30 MB or less</li>
      <li>Maximum size: 50 MB</li>
      <li>Large repositories may take longer to analyze.</li>
      <li>GitHub URL import coming soon.</li>
    </ul>
  );
}
