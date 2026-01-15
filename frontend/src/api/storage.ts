import client from './client';
import type { UploadResponse } from './types';

export function getImageUrl(imageId: string): string {
    return `/api/v1/storage/images/${imageId}`;
}

export async function uploadImage(
    file: File,
    options?: {
        tags?: string;
        description?: string;
        auto_index?: boolean;
        async_index?: boolean;
    },
    onProgress?: (progress: number) => void
): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.tags) formData.append('tags', options.tags);
    if (options?.description) formData.append('description', options.description);
    formData.append('auto_index', String(options?.auto_index ?? true));
    formData.append('async_index', String(options?.async_index ?? true));

    const { data } = await client.post('/storage/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
            if (e.total && onProgress) {
                onProgress(Math.round((e.loaded * 100) / e.total));
            }
        }
    });
    return data;
}

export async function deleteImage(imageId: string): Promise<void> {
    await client.delete(`/storage/images/${imageId}`);
}

export async function listImages(page: number = 1, pageSize: number = 20) {
    const { data } = await client.get('/storage/images', {
        params: { page, page_size: pageSize }
    });
    return data;
}
