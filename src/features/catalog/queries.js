import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../api/queryKeys.js';
import { UsersCatalogAPI } from '../../api/endpoints.js';

/**
 * Hook to fetch catalog products list
 */
export function useProductsQuery(params) {
  return useQuery({
    queryKey: queryKeys.products.list(params),
    queryFn: () => UsersCatalogAPI.getProducts(),
  });
}

/**
 * Hook to fetch active public finishes
 */
export function useFinishesQuery() {
  return useQuery({
    queryKey: queryKeys.finishes.public(),
    queryFn: () => UsersCatalogAPI.getFinishes(),
  });
}
