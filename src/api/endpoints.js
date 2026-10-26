/**
 * FanstudioAI API Endpoints
 * All fetch calls are defined here using /api/users/... and /api/admin/... paths.
 */
import { apiJson, apiClient } from './client.js';

// ==================== USERS STOREFRONT APIs ====================

export const UsersCatalogAPI = {
  getProducts: async () => {
    return apiJson('/api/users/products');
  },

  getProduct: async (productId) => {
    return apiJson(`/api/users/products/${encodeURIComponent(productId)}`);
  },

  getFinishes: async () => {
    return apiJson('/api/users/finishes');
  },

  getProductVariants: async (productId) => {
    return apiJson(`/api/users/products/${encodeURIComponent(productId)}/variants`);
  },

  resolveVariant: async (productId, motorFinishId, bladeFinishId) => {
    return apiJson(`/api/users/products/${encodeURIComponent(productId)}/resolve-variant`, {
      method: 'POST',
      body: {
        motor_finish_id: motorFinishId,
        blade_finish_id: bladeFinishId,
      },
    });
  },

  getCombinationImageUrl: (fanCode, motorColor, bladeColor) => {
    const params = new URLSearchParams({
      fan_code: fanCode || '',
      motor_color: motorColor || '',
      blade_color: bladeColor || '',
    });
    return `/api/users/combination-image?${params.toString()}`;
  },

  getFanCutoutUrl: (fanCode, motorColor, bladeColor) => {
    const params = new URLSearchParams({
      fan_code: fanCode || '',
      motor_color: motorColor || '',
      blade_color: bladeColor || '',
    });
    return `/api/users/fan-cutout?${params.toString()}`;
  },
};

export const UsersRoomsAPI = {
  uploadBase64: async (imageBase64, filename) => {
    return apiJson('/api/users/rooms/upload-base64', {
      method: 'POST',
      body: {
        image_base64: imageBase64,
        filename: filename || 'room.jpg',
      },
    });
  },

  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiJson('/api/users/rooms/upload', {
      method: 'POST',
      body: formData,
    });
  },

  getRoom: async (roomId) => {
    return apiJson(`/api/users/rooms/${encodeURIComponent(roomId)}`);
  },
};

export const UsersVisualizeAPI = {
  createJob: async (params) => {
    return apiJson('/api/users/visualize', {
      method: 'POST',
      body: params,
    });
  },

  getJob: async (jobId) => {
    return apiJson(`/api/users/visualize/${encodeURIComponent(jobId)}`);
  },

  getResult: async (jobId) => {
    return apiJson(`/api/users/visualize/${encodeURIComponent(jobId)}/result`);
  },
};

// ==================== ADMIN STUDIO APIs ====================

export const AdminProductsAPI = {
  list: async () => {
    return apiJson('/api/admin/products');
  },

  get: async (productId) => {
    return apiJson(`/api/admin/products/${encodeURIComponent(productId)}`);
  },

  create: async (productData) => {
    return apiJson('/api/admin/products', {
      method: 'POST',
      body: productData,
    });
  },

  update: async (productId, updates) => {
    return apiJson(`/api/admin/products/${encodeURIComponent(productId)}`, {
      method: 'PUT',
      body: updates,
    });
  },

  delete: async (productId) => {
    return apiJson(`/api/admin/products/${encodeURIComponent(productId)}`, {
      method: 'DELETE',
    });
  },

  batchImport: async (catalogPayload) => {
    return apiJson('/api/admin/products/batch-import', {
      method: 'POST',
      body: catalogPayload,
    });
  },

  reload: async () => {
    return apiJson('/api/admin/products/reload', {
      method: 'POST',
      body: {},
    });
  },
};

export const AdminFinishesAPI = {
  list: async (type = null, isActive = null) => {
    const params = new URLSearchParams();
    if (type) params.append('type', type);
    if (isActive !== null) params.append('is_active', String(isActive));
    const qs = params.toString() ? `?${params.toString()}` : '';
    return apiJson(`/api/admin/finishes${qs}`);
  },

  create: async (finishData) => {
    return apiJson('/api/admin/finishes', {
      method: 'POST',
      body: finishData,
    });
  },

  update: async (finishId, updates) => {
    return apiJson(`/api/admin/finishes/${encodeURIComponent(finishId)}`, {
      method: 'PUT',
      body: updates,
    });
  },

  deactivate: async (finishId) => {
    return apiJson(`/api/admin/finishes/${encodeURIComponent(finishId)}`, {
      method: 'DELETE',
    });
  },
};

export const AdminVariantsAPI = {
  listByProduct: async (productId) => {
    return apiJson(`/api/admin/products/${encodeURIComponent(productId)}/variants`);
  },

  create: async (productId, variantData) => {
    return apiJson(`/api/admin/products/${encodeURIComponent(productId)}/variants`, {
      method: 'POST',
      body: variantData,
    });
  },

  update: async (variantId, updates) => {
    return apiJson(`/api/admin/variants/${encodeURIComponent(variantId)}`, {
      method: 'PUT',
      body: updates,
    });
  },

  delete: async (variantId) => {
    return apiJson(`/api/admin/variants/${encodeURIComponent(variantId)}`, {
      method: 'DELETE',
    });
  },
};

export const AdminMediaAPI = {
  list: async (productId) => {
    return apiJson(`/api/admin/products/${encodeURIComponent(productId)}/media`);
  },

  upload: async (mediaPayload) => {
    return apiJson('/api/admin/media/upload', {
      method: 'POST',
      body: mediaPayload,
    });
  },

  setPrimary: async (mediaId) => {
    return apiJson(`/api/admin/media/${encodeURIComponent(mediaId)}/set-primary`, {
      method: 'PUT',
    });
  },

  delete: async (mediaId) => {
    return apiJson(`/api/admin/media/${encodeURIComponent(mediaId)}`, {
      method: 'DELETE',
    });
  },
};

export const AdminSystemAPI = {
  getStatus: async () => {
    return apiJson('/api/admin/mongodb/status');
  },

  getAuditLogs: async (limit = 100) => {
    return apiJson(`/api/admin/audit-logs?limit=${encodeURIComponent(limit)}`);
  },
};
