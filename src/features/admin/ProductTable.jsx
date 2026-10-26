import React from 'react';
import { Camera, Trash2, Plus, Search } from 'lucide-react';
import { Badge } from '../../components/Badge.jsx';
import { FanGraphic } from '../../components/FanGraphic.jsx';

export const ProductTable = ({
  products,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  onOpenAddProduct,
  onOpenUploadPhoto,
  onDeleteProduct,
}) => {
  const filteredProducts = products.filter((p) => {
    if (statusFilter !== 'All' && p.status !== statusFilter.toLowerCase()) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const matchName = (p.name || p.fanName || '').toLowerCase().includes(q);
      const matchCode = (p.product_code || p.fanCode || '').toLowerCase().includes(q);
      const matchCat = (p.category || '').toLowerCase().includes(q);
      if (!matchName && !matchCode && !matchCat) return false;
    }
    return true;
  });

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs overflow-hidden">
      {/* Table Header & Controls */}
      <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search products..."
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
          </div>

          <div className="flex gap-1 bg-slate-100 p-1 rounded-xl">
            {['All', 'Active', 'Inactive'].map((s) => (
              <button
                key={s}
                onClick={() => onStatusFilterChange(s)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  statusFilter === s
                    ? 'bg-white text-slate-900 shadow-2xs font-bold'
                    : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={onOpenAddProduct}
          className="w-full sm:w-auto px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-xs transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Add Product</span>
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/80 text-slate-500 border-b border-slate-100 font-bold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-4">Photo / Model</th>
              <th className="py-3 px-4">Product Code</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Blade Spec</th>
              <th className="py-3 px-4">Price</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
            {filteredProducts.map((p) => {
              const rawImg = p.primary_image_url || p.imagePath || (p.images && p.images[0]);
              const displayImg = rawImg ? (rawImg.startsWith('http') ? rawImg : `/${rawImg.replace(/^\//, '')}`) : null;

              return (
                <tr key={p.product_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 overflow-hidden flex items-center justify-center shrink-0">
                        {displayImg ? (
                          <img src={displayImg} alt={p.name} className="w-full h-full object-contain" />
                        ) : (
                          <div className="w-8 h-8">
                            <FanGraphic bladeCount={p.blade_count || 3} />
                          </div>
                        )}
                      </div>
                      <div>
                        <div className="font-bold text-slate-900 line-clamp-1">{p.name || p.fanName}</div>
                        <div className="text-[10px] text-slate-400">
                          {p.motor_colors?.length || 0} motors • {p.blade_colors?.length || 0} blades
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-slate-500">
                    {p.product_code || p.fanCode}
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant="default" size="xs">
                      {p.category || 'Ceiling'}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-slate-600">
                    {p.blade_count || 3} Blades • {p.blade_type || 'Timber'}
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">
                    ₹{Number(p.price || p.base_price || 0).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <Badge
                      variant={p.status === 'active' ? 'success' : 'default'}
                      size="xs"
                      dot
                      dotColor={p.status === 'active' ? '#10B981' : '#94A3B8'}
                    >
                      {p.status || 'active'}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <button
                        onClick={() => onOpenUploadPhoto(p)}
                        title="Upload Product Photo"
                        className="p-1.5 rounded-lg text-slate-500 hover:text-amber-700 hover:bg-amber-50 transition-colors cursor-pointer"
                      >
                        <Camera className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => onDeleteProduct(p.product_id)}
                        title="Delete / Deactivate"
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
