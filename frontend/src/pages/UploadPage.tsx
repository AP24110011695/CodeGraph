import { PageNavbar } from './shared/components';
import { UploadCard, UploadInfoCards, GitHubImport, ProcessSteps } from './upload/components';
import { useUpload } from '@/features/upload/hooks/useUpload';
import { Button } from '@/design-system/primitives/Button';

export default function UploadPage() {
  const { startUpload, reset, isUploading, error } = useUpload();

  return (
    <div className="min-h-screen bg-bg-base">
      <div
        className="fixed inset-0 -z-10"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(232, 160, 69, 0.03) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(232, 160, 69, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '64px 64px',
        }}
      />
      <PageNavbar backHref="/" />

      <main className="mx-auto max-w-[1280px] px-6 pb-16 pt-8">
        <div className="mb-8 space-y-2">
          <h1 className="text-3xl font-medium text-text-primary">Upload a repository</h1>
          <p className="text-base text-text-secondary">
            Drop a ZIP archive to analyze your project architecture.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[65%_35%]">
          <div className="space-y-6">
            <UploadCard
              disabled={isUploading}
              error={error}
              onFileSelected={(file) => {
                void startUpload(file);
              }}
            />

            {error && (
              <div className="space-y-3 rounded-xl border border-danger/30 bg-danger/10 p-4">
                <p className="text-sm text-danger">{error}</p>
                <Button variant="danger" size="sm" onClick={reset}>
                  Retry
                </Button>
              </div>
            )}

            <UploadInfoCards />
            <GitHubImport />
          </div>

          <div className="space-y-6">
            <ProcessSteps />
          </div>
        </div>
      </main>
    </div>
  );
}
