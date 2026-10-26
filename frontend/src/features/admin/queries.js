import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../../api/queryKeys.js';
import {
  AdminProductsAPI,
  AdminFinishesAPI,
  AdminVariantsAPI,
  AdminMediaAPI,
  AdminSystemAPI,
} from '../../api/endpoints.js';

// ==================== ADMIN QUERIES ====================

export function useAdminProductsQuery() {
  return useQuery({
    queryKey: queryKeys.admin.products(),
    queryFn: () => AdminProductsAPI.list(),
  });
}

export function useAdminFinishesQuery(params) {
  return useQuery({
    queryKey: queryKeys.admin.finishes(params),
    queryFn: () => AdminFinishesAPI.list(params?.type, params?.isActive),
  });
}

export function useAuditLogsQuery(limit = 100) {
  return useQuery({
    queryKey: queryKeys.admin.auditLogs(limit),
    queryFn: () => AdminSystemAPI.getAuditLogs(limit),
  });
}

export function useMongoStatusQuery() {
  return useQuery({
    queryKey: queryKeys.admin.mongoStatus(),
    queryFn: () => AdminSystemAPI.getStatus(),
  });
}

// ==================== PRODUCT MUTATIONS ====================

export function useCreateProductMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (productData) => AdminProductsAPI.create(productData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useUpdateProductMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, updates }) => AdminProductsAPI.update(productId, updates),
    onSuccess: (_data, { productId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.detail(productId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useToggleProductStatusMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, status }) => AdminProductsAPI.update(productId, { status }),
    onSuccess: (_data, { productId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.detail(productId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
    },
  });
}

export function useDeleteProductMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (productId) => AdminProductsAPI.delete(productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

// ==================== FINISH MUTATIONS ====================

export function useCreateFinishMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (finishData) => AdminFinishesAPI.create(finishData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.finishes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.finishes.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useUpdateFinishMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ finishId, updates }) => AdminFinishesAPI.update(finishId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.finishes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.finishes.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useToggleFinishStatusMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ finishId, isActive }) => AdminFinishesAPI.update(finishId, { is_active: isActive }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.finishes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.finishes.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useDeleteFinishMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (finishId) => AdminFinishesAPI.deactivate(finishId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.finishes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.finishes.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

// ==================== VARIANT MUTATIONS ====================

export function useCreateVariantMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ productId, variantData }) => AdminVariantsAPI.create(productId, variantData),
    onSuccess: (_data, { productId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.variants(productId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.variants(productId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.detail(productId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useUpdateVariantMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ variantId, updates }) => AdminVariantsAPI.update(variantId, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
    },
  });
}

export function useDeleteVariantMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (variantId) => AdminVariantsAPI.delete(variantId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
    },
  });
}

// ==================== MEDIA MUTATIONS ====================

export function useUploadMediaMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (mediaPayload) => AdminMediaAPI.upload(mediaPayload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      if (variables?.product_id) {
        queryClient.invalidateQueries({ queryKey: queryKeys.admin.media(variables.product_id) });
        queryClient.invalidateQueries({ queryKey: queryKeys.products.detail(variables.product_id) });
      }
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

// ==================== BATCH & RELOAD MUTATIONS ====================

export function useBatchImportMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (catalogPayload) => AdminProductsAPI.batchImport(catalogPayload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}

export function useReloadCatalogMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => AdminProductsAPI.reload(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.products() });
      queryClient.invalidateQueries({ queryKey: queryKeys.products.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.finishes() });
      queryClient.invalidateQueries({ queryKey: queryKeys.finishes.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.auditLogs() });
    },
  });
}
