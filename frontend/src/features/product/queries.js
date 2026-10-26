import { useQuery, useMutation } from '@tanstack/react-query';
import { queryKeys } from '../../api/queryKeys.js';
import { UsersCatalogAPI } from '../../api/endpoints.js';

/**
 * Hook to fetch single product details
 */
export function useProductQuery(productId) {
  return useQuery({
    queryKey: queryKeys.products.detail(productId),
    queryFn: () => UsersCatalogAPI.getProduct(productId),
    enabled: !!productId,
  });
}

/**
 * Hook to fetch registered product variants
 */
export function useVariantsQuery(productId) {
  return useQuery({
    queryKey: queryKeys.products.variants(productId),
    queryFn: () => UsersCatalogAPI.getProductVariants(productId),
    enabled: !!productId,
  });
}

/**
 * Hook to resolve custom finish combination against catalog rules
 */
export function useResolveVariantMutation() {
  return useMutation({
    mutationFn: ({ productId, motorFinishId, bladeFinishId }) =>
      UsersCatalogAPI.resolveVariant(productId, motorFinishId, bladeFinishId),
  });
}
