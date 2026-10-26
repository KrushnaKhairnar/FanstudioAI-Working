import { create } from 'zustand';

export const PRESET_ROOMS = [
  {
    id: 'room-living-01',
    name: 'Modern Minimalist Living',
    imageUrl: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80',
    ceilingX: 0.50,
    ceilingY: 0.22,
  },
  {
    id: 'room-scandi-02',
    name: 'Scandinavian Dining Space',
    imageUrl: 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=80',
    ceilingX: 0.48,
    ceilingY: 0.20,
  },
  {
    id: 'room-master-03',
    name: 'Master Suite Bedroom',
    imageUrl: 'https://images.unsplash.com/photo-1540518614846-7ede433c4550?auto=format&fit=crop&w=1200&q=80',
    ceilingX: 0.52,
    ceilingY: 0.24,
  },
];

const INITIAL_PLACEMENT_STATE = {
  anchorX: 0.50,
  anchorY: 0.22,
  scale: 1.1,
  rotation: 0,
  downrodLength: 12,
  brightness: 0.85,
  colorTemp: 4200,
  applyShadow: true,
  applyLighting: true,
  renderedImageUrl: null,
  renderTimeMs: null,
  jobStatus: 'IDLE',
  errorMessage: null,
  activeJobId: null,
  showComparison: false,
  compareSplit: 50,
};

const INITIAL_VISUALIZER_STATE = {
  selectedRoomId: PRESET_ROOMS[0].id,
  roomImage: PRESET_ROOMS[0].imageUrl,
  customRooms: [],
  selectedProductCode: null,
  selectedMotorId: null,
  selectedBladeId: null,
  ...INITIAL_PLACEMENT_STATE,
};

export const useVisualizerStore = create((set) => ({
  ...INITIAL_VISUALIZER_STATE,

  setSelectedRoom: (room) =>
    set({
      selectedRoomId: room.id,
      roomImage: room.imageUrl,
      anchorX: room.ceilingX ?? 0.50,
      anchorY: room.ceilingY ?? 0.22,
      renderedImageUrl: null,
      jobStatus: 'IDLE',
      activeJobId: null,
    }),

  addCustomRoom: (newRoom) =>
    set((state) => ({
      customRooms: [newRoom, ...state.customRooms],
      selectedRoomId: newRoom.id,
      roomImage: newRoom.imageUrl,
      anchorX: newRoom.ceilingX ?? 0.50,
      anchorY: newRoom.ceilingY ?? 0.22,
      renderedImageUrl: null,
      jobStatus: 'IDLE',
      activeJobId: null,
    })),

  setSelectedProductCode: (selectedProductCode) => set({ selectedProductCode }),
  setSelectedMotorId: (selectedMotorId) => set({ selectedMotorId }),
  setSelectedBladeId: (selectedBladeId) => set({ selectedBladeId }),

  setAnchor: (anchorX, anchorY) => set({ anchorX, anchorY }),
  setScale: (scale) => set({ scale }),
  setRotation: (rotation) => set({ rotation }),
  setDownrodLength: (downrodLength) => set({ downrodLength }),
  setBrightness: (brightness) => set({ brightness }),
  setColorTemp: (colorTemp) => set({ colorTemp }),
  setApplyShadow: (applyShadow) => set({ applyShadow }),
  setApplyLighting: (applyLighting) => set({ applyLighting }),
  setShowComparison: (showComparison) => set({ showComparison }),
  setCompareSplit: (compareSplit) => set({ compareSplit }),

  setRenderedResult: ({ url, renderTimeMs }) =>
    set({
      renderedImageUrl: url,
      renderTimeMs: renderTimeMs ?? null,
      jobStatus: 'SUCCESS',
      activeJobId: null,
    }),

  setJobStatus: (jobStatus) => set({ jobStatus }),
  setErrorMessage: (errorMessage) => set({ errorMessage }),
  setActiveJobId: (activeJobId) => set({ activeJobId }),

  resetPlacement: () =>
    set((state) => ({
      ...INITIAL_PLACEMENT_STATE,
      // Retain the current room's default ceiling coordinates if available
      anchorX: 0.50,
      anchorY: 0.22,
    })),

  resetVisualizer: () => set({ ...INITIAL_VISUALIZER_STATE }),
}));
