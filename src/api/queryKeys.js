/**
 * Query Key Factory for TanStack Query
 */
export const queryKeys = {
  products: {
    all: ['products'],
    list: (params) => ['products', 'list', params ?? null],
    detail: (id) => ['products', 'detail', id],
    variants: (id) => ['products', 'variants', id],
  },
  finishes: {
    all: ['finishes'],
    public: () => ['finishes', 'public'],
  },
  visualize: {
    all: ['visualize'],
    job: (id) => ['visualize', 'job', id],
    result: (id) => ['visualize', 'result', id],
  },
  rooms: {
    all: ['rooms'],
    detail: (id) => ['rooms', 'detail', id],
  },
  admin: {
    all: ['admin'],
    products: () => ['admin', 'products'],
    finishes: (params) => ['admin', 'finishes', params ?? null],
    variants: (productId) => ['admin', 'variants', productId],
    media: (productId) => ['admin', 'media', productId],
    auditLogs: (limit = 100) => ['admin', 'auditLogs', limit],
    mongoStatus: () => ['admin', 'mongoStatus'],
  },
};
