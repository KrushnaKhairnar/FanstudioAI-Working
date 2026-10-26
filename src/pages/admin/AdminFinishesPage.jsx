import React, { useMemo } from 'react';
import { useAdminFinishesQuery } from '../../features/admin/queries.js';
import { FinishesManager } from '../../features/admin/FinishesManager.jsx';

export const AdminFinishesPage = () => {
  const { data: rawFinishes = [] } = useAdminFinishesQuery();
  const finishesList = useMemo(
    () => (Array.isArray(rawFinishes) ? rawFinishes : []),
    [rawFinishes]
  );

  return (
    <div className="p-6 sm:p-8">
      <FinishesManager finishesList={finishesList} />
    </div>
  );
};
