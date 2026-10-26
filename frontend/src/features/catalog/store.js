import { create } from 'zustand';

const INITIAL_CATALOG_FILTERS = {
  searchQuery: '',
  sortBy: 'Popular',
  selectedCategory: 'All Fans',
  selectedBladeCounts: [],
  selectedMotorColor: null,
  selectedBladeColor: null,
  priceMax: 30000,
};

export const useCatalogStore = create((set) => ({
  ...INITIAL_CATALOG_FILTERS,

  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSortBy: (sortBy) => set({ sortBy }),
  setSelectedCategory: (selectedCategory) => set({ selectedCategory }),
  setSelectedBladeCounts: (bladeCountsOrFn) =>
    set((state) => ({
      selectedBladeCounts:
        typeof bladeCountsOrFn === 'function'
          ? bladeCountsOrFn(state.selectedBladeCounts)
          : bladeCountsOrFn,
    })),
  toggleBladeCount: (count) =>
    set((state) => ({
      selectedBladeCounts: state.selectedBladeCounts.includes(count)
        ? state.selectedBladeCounts.filter((c) => c !== count)
        : [...state.selectedBladeCounts, count],
    })),
  setSelectedMotorColor: (selectedMotorColor) => set({ selectedMotorColor }),
  setSelectedBladeColor: (selectedBladeColor) => set({ selectedBladeColor }),
  setPriceMax: (priceMax) => set({ priceMax }),

  resetFilters: () => set({ ...INITIAL_CATALOG_FILTERS }),
}));
