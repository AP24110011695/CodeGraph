import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAPIError } from '@/core/api/errors';
import { useUploadMutation } from '../api/upload.queries';
import { validateZipFile } from '../api/upload.types';

export function useUpload() {
  const navigate = useNavigate();
  const mutation = useUploadMutation();
  const [progress, setProgress] = useState(0);
  const [localError, setLocalError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setProgress(0);
    setLocalError(null);
    mutation.reset();
  }, [mutation]);

  const startUpload = useCallback(
    async (file: File) => {
      const validationError = validateZipFile(file);
      if (validationError) {
        setLocalError(validationError);
        return;
      }

      setLocalError(null);
      setProgress(0);

      try {
        const result = await mutation.mutateAsync({
          file,
          onProgress: setProgress,
        });
        setProgress(100);
        navigate(`/indexing/${result.upload_id}`);
      } catch (error) {
        const message = isAPIError(error)
          ? error.message
          : error instanceof Error
            ? error.message
            : 'Upload failed. Please try again.';
        setLocalError(message);
      }
    },
    [mutation, navigate]
  );

  return {
    startUpload,
    reset,
    progress,
    isUploading: mutation.isPending,
    error: localError,
    isError: Boolean(localError) || mutation.isError,
    isSuccess: mutation.isSuccess,
  };
}
