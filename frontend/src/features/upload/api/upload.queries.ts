import { useMutation, useQueryClient } from '@tanstack/react-query';
import { isAPIError } from '@/core/api/errors';
import { useRepositoryStore } from '@/core/store/repository.store';
import { repositoryKeys } from '@/features/repository';
import { uploadZipArchive } from './upload.api';
import { validateZipFile } from './upload.types';

interface UploadVariables {
  file: File;
  onProgress?: (percent: number) => void;
}

export function useUploadMutation() {
  const queryClient = useQueryClient();
  const setActiveRepository = useRepositoryStore((s) => s.setActiveRepository);
  const setIndexingStatus = useRepositoryStore((s) => s.setIndexingStatus);

  return useMutation({
    mutationKey: ['upload', 'zip'],
    mutationFn: async ({ file, onProgress }: UploadVariables) => {
      const validationError = validateZipFile(file);
      if (validationError) {
        throw { code: 'validation_error', message: validationError, status: 400 };
      }

      setIndexingStatus('uploading');
      return uploadZipArchive(file, onProgress);
    },
    onSuccess: (data, variables) => {
      const name = variables.file.name.replace(/\.zip$/i, '') || data.filename;
      setActiveRepository(data.upload_id, {
        id: data.upload_id,
        name,
        source: 'zip',
        uploadedAt: new Date().toISOString(),
        filename: data.filename,
      });
      setIndexingStatus('pending');
      void queryClient.invalidateQueries({ queryKey: repositoryKeys.all });
    },
    onError: (error) => {
      setIndexingStatus('error');
      if (!isAPIError(error)) return;
    },
  });
}
