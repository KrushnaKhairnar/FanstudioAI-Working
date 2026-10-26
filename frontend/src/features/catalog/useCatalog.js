import { useMemo, useCallback, useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useProductsQuery, useFinishesQuery } from './queries.js';
import { useCatalogStore } from './store.js';

export function useCatalog(initialSearch = '') {
  const {
    data: rawProducts = [],
    isLoading: isProductsLoading,
    error: productsError,
    refetch: refetchProducts,
  } = useProductsQuery();

  const {
    data: rawFinishes = [],
    isLoading: isFinishesLoading,
    error: finishesError,
    refetch: refetchFinishes,
  } = useFinishesQuery();

  const products = useMemo(() => (Array.isArray(rawProducts) ? rawProducts : []), [rawProducts]);
  const finishes = useMemo(() => (Array.isArray(rawFinishes) ? rawFinishes : []), [rawFinishes]);
  const isLoading = isProductsLoading || isFinishesLoading;
  const error = productsError?.message || finishesError?.message || null;

  // Select UI filters state and actions from useCatalogStore
  const {
    searchQuery,
    sortBy,
    selectedCategory,
    selectedBladeCounts,
    selectedMotorColor,
    selectedBladeColor,
    priceMax,
    setSearchQuery,
    setSortBy,
    setSelectedCategory,
    setSelectedBladeCounts,
    toggleBladeCount,
    setSelectedMotorColor,
    setSelectedBladeColor,
    setPriceMax,
    resetFilters,
  } = useCatalogStore(
    useShallow((s) => ({
      searchQuery: s.searchQuery,
      sortBy: s.sortBy,
      selectedCategory: s.selectedCategory,
      selectedBladeCounts: s.selectedBladeCounts,
      selectedMotorColor: s.selectedMotorColor,
      selectedBladeColor: s.selectedBladeColor,
      priceMax: s.priceMax,
      setSearchQuery: s.setSearchQuery,
      setSortBy: s.setSortBy,
      setSelectedCategory: s.setSelectedCategory,
      setSelectedBladeCounts: s.setSelectedBladeCounts,
      toggleBladeCount: s.toggleBladeCount,
      setSelectedMotorColor: s.setSelectedMotorColor,
      setSelectedBladeColor: s.setSelectedBladeColor,
      setPriceMax: s.setPriceMax,
      resetFilters: s.resetFilters,
    }))
  );

  useEffect(() => {
    if (initialSearch && !searchQuery) {
      setSearchQuery(initialSearch);
    }
  }, [initialSearch, searchQuery, setSearchQuery]);

  // Dynamic filter options derived from products catalog
  const dynamicCategories = useMemo(() => {
    const cats = new Set();
    products.forEach((p) => {
      if (p.category) cats.add(p.category);
    });
    return ['All Fans', ...Array.from(cats)];
  }, [products]);

  const dynamicBladeCounts = useMemo(() => {
    const countsMap = new Map();
    products.forEach((p) => {
      const bc = p.blade_count || 3;
      countsMap.set(bc, (countsMap.get(bc) || 0) + 1);
    });
    return Array.from(countsMap.entries())
      .map(([count, total]) => ({ count, total }))
      .sort((a, b) => a.count - b.count);
  }, [products]);

  const dynamicMotorColors = useMemo(() => {
    const colors = new Set();
    products.forEach((p) => {
      if (p.motor_colors && Array.isArray(p.motor_colors)) {
        p.motor_colors.forEach((c) => colors.add(c));
      } else if (p.default_motor_color) {
        colors.add(p.default_motor_color);
      }
    });
    return Array.from(colors);
  }, [products]);

  const dynamicBladeColors = useMemo(() => {
    const colors = new Set();
    products.forEach((p) => {
      if (p.blade_colors && Array.isArray(p.blade_colors)) {
        p.blade_colors.forEach((c) => colors.add(c));
      } else if (p.default_blade_color) {
        colors.add(p.default_blade_color);
      }
    });
    return Array.from(colors);
  }, [products]);

  // Filtering & Sorting logic
  const filteredProducts = useMemo(() => {
    return products
      .filter((fan) => {
        // Category
        if (selectedCategory !== 'All Fans' && fan.category !== selectedCategory) {
          return false;
        }

        // Blade Count
        if (selectedBladeCounts.length > 0 && !selectedBladeCounts.includes(fan.blade_count || 3)) {
          return false;
        }

        // Motor Finish
        if (selectedMotorColor) {
          const hasColor =
            fan.motor_colors?.includes(selectedMotorColor) ||
            fan.default_motor_color === selectedMotorColor;
          if (!hasColor) return false;
        }

        // Blade Finish
        if (selectedBladeColor) {
          const hasColor =
            fan.blade_colors?.includes(selectedBladeColor) ||
            fan.default_blade_color === selectedBladeColor;
          if (!hasColor) return false;
        }

        // Price
        const priceVal = fan.price || fan.base_price || 0;
        if (priceVal > priceMax) return false;

        // Search Query
        if (searchQuery.trim()) {
          const query = searchQuery.toLowerCase().trim();
          const matchName = (fan.name || fan.fanName || '').toLowerCase().includes(query);
          const matchCode = (fan.product_code || fan.fanCode || '').toLowerCase().includes(query);
          const matchCategory = (fan.category || '').toLowerCase().includes(query);
          const matchDesc = (fan.description || '').toLowerCase().includes(query);
          if (!matchName && !matchCode && !matchCategory && !matchDesc) {
            return false;
          }
        }

        return true;
      })
      .sort((a, b) => {
        const priceA = a.price || a.base_price || 0;
        const priceB = b.price || b.base_price || 0;
        if (sortBy === 'Price: Low to High') return priceA - priceB;
        if (sortBy === 'Price: High to Low') return priceB - priceA;
        if (sortBy === 'Name: A-Z') return (a.name || '').localeCompare(b.name || '');
        return 0; // Default Popular / Catalog sequence
      });
  }, [
    products,
    selectedCategory,
    selectedBladeCounts,
    selectedMotorColor,
    selectedBladeColor,
    priceMax,
    searchQuery,
    sortBy,
  ]);

  const refresh = useCallback(() => {
    refetchProducts();
    refetchFinishes();
  }, [refetchProducts, refetchFinishes]);

  return {
    products,
    finishes,
    isLoading,
    error,
    refresh,
    filteredProducts,
    // Filter controls
    selectedCategory,
    setSelectedCategory,
    selectedBladeCounts,
    setSelectedBladeCounts,
    toggleBladeCount,
    selectedMotorColor,
    setSelectedMotorColor,
    selectedBladeColor,
    setSelectedBladeColor,
    priceMax,
    setPriceMax,
    sortBy,
    setSortBy,
    searchQuery,
    setSearchQuery,
    resetFilters,
    // Dynamic lists
    dynamicCategories,
    dynamicBladeCounts,
    dynamicMotorColors,
    dynamicBladeColors,
  };
}
