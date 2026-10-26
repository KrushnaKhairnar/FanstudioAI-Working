import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import { UserLayout } from '../components/layouts/UserLayout.jsx';
import { AdminLayout } from '../components/layouts/AdminLayout.jsx';

// Customer Pages
import { CatalogPage } from '../pages/users/CatalogPage.jsx';
import { ProductDetailPage } from '../pages/users/ProductDetailPage.jsx';
import { VisualizerPage } from '../pages/users/VisualizerPage.jsx';

// Admin Pages
import { AdminProductsPage } from '../pages/admin/AdminProductsPage.jsx';
import { AdminFinishesPage } from '../pages/admin/AdminFinishesPage.jsx';
import { AdminImportPage } from '../pages/admin/AdminImportPage.jsx';
import { AdminAuditLogsPage } from '../pages/admin/AdminAuditLogsPage.jsx';

export default function App() {
  return (
    <Routes>
      {/* Root redirects to /users */}
      <Route path="/" element={<Navigate to="/users" replace />} />

      {/* Customer Storefront Routes */}
      <Route path="/users" element={<UserLayout />}>
        <Route index element={<CatalogPage />} />
        <Route path="products/:id" element={<ProductDetailPage />} />
        <Route path="visualizer" element={<VisualizerPage />} />
      </Route>

      {/* Admin Studio Routes */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<AdminProductsPage />} />
        <Route path="finishes" element={<AdminFinishesPage />} />
        <Route path="import" element={<AdminImportPage />} />
        <Route path="audit-logs" element={<AdminAuditLogsPage />} />
      </Route>

      {/* Catch-all redirect to /users */}
      <Route path="*" element={<Navigate to="/users" replace />} />
    </Routes>
  );
}
