import { create } from 'zustand';

const INITIAL_PRODUCT_STATE = {
  selectedMotorId: '',
  selectedBladeId: '',
  selectedBladeSize: '',
  selectedFanType: '',
  selectedColorIdx: 0,
  selectedThumb: 0,
  quantity: 1,
};

export const useProductStore = create((set) => ({
  ...INITIAL_PRODUCT_STATE,

  setSelectedMotorId: (selectedMotorId) => set({ selectedMotorId }),
  setSelectedBladeId: (selectedBladeId) => set({ selectedBladeId }),
  setSelectedBladeSize: (selectedBladeSize) => set({ selectedBladeSize }),
  setSelectedFanType: (selectedFanType) => set({ selectedFanType }),
  setSelectedColorIdx: (selectedColorIdx) => set({ selectedColorIdx }),
  setSelectedThumb: (selectedThumb) => set({ selectedThumb }),
  setQuantity: (quantity) => set({ quantity }),

  resetProductState: () => set({ ...INITIAL_PRODUCT_STATE }),
}));
