import { create } from "zustand";

type DashboardState = {
  repProductId: string | null;
  setRepProductId: (id: string | null) => void;
};

export const useDashboardStore = create<DashboardState>()((set) => ({
  repProductId: null,
  setRepProductId: (id) => set({ repProductId: id }),
}));
