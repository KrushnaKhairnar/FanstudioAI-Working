import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCatalog } from '../../features/catalog/useCatalog.js';
import { CatalogFilters } from '../../features/catalog/CatalogFilters.jsx';
import { CatalogSearch } from '../../features/catalog/CatalogSearch.jsx';
import { ProductCard } from '../../features/catalog/ProductCard.jsx';
import { NoData } from '../../components/NoData.jsx';
import { Loader2 } from 'lucide-react';

export const CatalogPage = () => {
  const navigate = useNavigate();

  const {
    isLoading,
    filteredProducts,
    selectedCategory,
    setSelectedCategory,
    selectedBladeCounts,
    setSelectedBladeCounts,
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
    dynamicCategories,
    dynamicBladeCounts,
    dynamicMotorColors,
    dynamicBladeColors,
  } = useCatalog();

  const handleToggleBladeCount = (count) => {
    setSelectedBladeCounts((prev) =>
      prev.includes(count) ? prev.filter((c) => c !== count) : [...prev, count]
    );
  };

  const handleSelectProduct = (product) => {
    const id = product.product_id || product.productId;
    navigate(`/users/products/${encodeURIComponent(id)}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleOpenVisualizer = (product) => {
    const id = product.product_id || product.productId;
    const motor = product.default_motor_color || product.motor_finish_ids?.[0] || '';
    const blade = product.default_blade_color || product.blade_finish_ids?.[0] || '';
    navigate(`/users/visualizer?product=${encodeURIComponent(id)}&motor=${encodeURIComponent(motor)}&blade=${encodeURIComponent(blade)}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        {/* Left Sidebar Filter Rail */}
        <aside className="w-full lg:w-72 shrink-0">
          <CatalogFilters
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
            dynamicCategories={dynamicCategories}
            selectedBladeCounts={selectedBladeCounts}
            onToggleBladeCount={handleToggleBladeCount}
            dynamicBladeCounts={dynamicBladeCounts}
            selectedMotorColor={selectedMotorColor}
            onSelectMotorColor={setSelectedMotorColor}
            dynamicMotorColors={dynamicMotorColors}
            selectedBladeColor={selectedBladeColor}
            onSelectBladeColor={setSelectedBladeColor}
            dynamicBladeColors={dynamicBladeColors}
            priceMax={priceMax}
            onChangePriceMax={setPriceMax}
            onResetFilters={resetFilters}
          />
        </aside>

        {/* Right Main Catalog Content */}
        <div className="flex-1 min-w-0 space-y-6">
          <CatalogSearch
            totalResults={filteredProducts.length}
            selectedCategory={selectedCategory}
            sortBy={sortBy}
            onSortChange={setSortBy}
          />

          {isLoading ? (
            <div className="py-24 flex flex-col items-center justify-center text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-amber-600 mb-2" />
              <p className="text-xs font-semibold">Loading ceiling fan models...</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <NoData
              title="No Ceiling Fans Matched"
              description="No fan models match your active filters and search criteria. Try resetting your filters."
              actionLabel="Reset All Filters"
              onAction={resetFilters}
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredProducts.map((fan) => (
                <ProductCard
                  key={fan.product_id || fan.productId}
                  fan={fan}
                  onSelectProduct={handleSelectProduct}
                  onOpenVisualizer={handleOpenVisualizer}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
