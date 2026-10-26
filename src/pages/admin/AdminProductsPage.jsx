import React, { useState, useMemo } from 'react';
import {
  useAdminProductsQuery,
  useAdminFinishesQuery,
  useDeleteProductMutation,
} from '../../features/admin/queries.js';
import { AdminDashboardOverview } from '../../features/admin/AdminDashboardOverview.jsx';
import { ProductTable } from '../../features/admin/ProductTable.jsx';
import { ProductForm } from '../../features/admin/ProductForm.jsx';
import { MediaUploadModal } from '../../features/admin/MediaUploadModal.jsx';
import { ConfirmDialog } from '../../components/ConfirmDialog.jsx';

export const AdminProductsPage = () => {
  const { data: rawProducts = [] } = useAdminProductsQuery();
  const { data: rawFinishes = [] } = useAdminFinishesQuery();
  const deleteProductMutation = useDeleteProductMutation();

  const productsList = useMemo(
    () => (Array.isArray(rawProducts) ? rawProducts : []),
    [rawProducts]
  );
  const finishesList = useMemo(
    () => (Array.isArray(rawFinishes) ? rawFinishes : []),
    [rawFinishes]
  );

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Modals state
  const [isAddProductOpen, setIsAddProductOpen] = useState(false);
  const [isUploadPhotoOpen, setIsUploadPhotoOpen] = useState(false);
  const [uploadTargetProduct, setUploadTargetProduct] = useState(null);

  // Confirm delete dialog
  const [deleteTargetId, setDeleteTargetId] = useState(null);

  const handleOpenUploadPhoto = (product) => {
    setUploadTargetProduct(product);
    setIsUploadPhotoOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deleteTargetId) return;
    try {
      await deleteProductMutation.mutateAsync(deleteTargetId);
    } catch (err) {
      console.error('Delete error:', err);
    } finally {
      setDeleteTargetId(null);
    }
  };

  return (
    <div className="p-6 sm:p-8 space-y-8">
      {/* Overview Stat Cards */}
      <AdminDashboardOverview
        productsCount={productsList.length}
        finishesCount={finishesList.length}
      />

      {/* Main Products Table */}
      <ProductTable
        products={productsList}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        onOpenAddProduct={() => setIsAddProductOpen(true)}
        onOpenUploadPhoto={handleOpenUploadPhoto}
        onDeleteProduct={(id) => setDeleteTargetId(id)}
      />

      {/* Add Product Modal Form */}
      <ProductForm
        isOpen={isAddProductOpen}
        onClose={() => setIsAddProductOpen(false)}
        finishesList={finishesList}
      />

      {/* Upload Media Modal */}
      <MediaUploadModal
        isOpen={isUploadPhotoOpen}
        onClose={() => setIsUploadPhotoOpen(false)}
        targetProduct={uploadTargetProduct}
      />

      {/* Confirm Deletion Dialog */}
      <ConfirmDialog
        isOpen={!!deleteTargetId}
        title="Deactivate / Delete Fan Model"
        message="Are you sure you want to delete this ceiling fan model? It will be removed or marked inactive in the database."
        confirmText="Delete Fan"
        isDestructive
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteTargetId(null)}
      />
    </div>
  );
};
