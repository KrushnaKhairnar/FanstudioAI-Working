import React, { useMemo } from 'react';
import { FileText, RefreshCw } from 'lucide-react';
import { Badge } from '../../components/Badge.jsx';
import { useAuditLogsQuery } from './queries.js';

export const AuditLogsTable = () => {
  const { data: rawLogs = [], isLoading, isFetching, refetch } = useAuditLogsQuery(100);
  const logs = useMemo(
    () => (Array.isArray(rawLogs) ? rawLogs : []),
    [rawLogs]
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs overflow-hidden">
      <div className="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-600" />
            <span>Audit Trail Event Logs</span>
          </h2>
          <p className="text-[11px] text-slate-500 mt-0.5">
            System modifications, catalog imports, and product records history
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isLoading || isFetching}
          className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading || isFetching ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/80 text-slate-500 border-b border-slate-100 font-bold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-4">Timestamp (UTC)</th>
              <th className="py-3 px-4">Action</th>
              <th className="py-3 px-4">Entity Type</th>
              <th className="py-3 px-4">Entity ID</th>
              <th className="py-3 px-4">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
            {logs.map((log, idx) => (
              <tr key={log.id || idx} className="hover:bg-slate-50/60 transition-colors">
                <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                  {log.timestamp ? new Date(log.timestamp).toLocaleString() : 'Recent'}
                </td>
                <td className="py-3 px-4">
                  <Badge variant="warning" size="xs">
                    {log.action}
                  </Badge>
                </td>
                <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                  {log.entity_type}
                </td>
                <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                  {log.entity_id || '—'}
                </td>
                <td className="py-3 px-4 text-slate-500 text-[11px] max-w-xs truncate">
                  {typeof log.details === 'object' ? JSON.stringify(log.details) : String(log.details || '—')}
                </td>
              </tr>
            ))}
            {logs.length === 0 && !isLoading && (
              <tr>
                <td colSpan="5" className="py-8 text-center text-slate-400">
                  No audit logs recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
