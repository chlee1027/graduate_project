import { create } from "zustand";

interface UserState {
  userId: string | null;
  isOnboarded: boolean;
  setUserId: (id: string) => void;
  setIsOnboarded: (status: boolean) => void;
  reset: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  userId: null,
  isOnboarded: false,
  setUserId: (id) => set({ userId: id }),
  setIsOnboarded: (status) => set({ isOnboarded: status }),
  reset: () => set({ userId: null, isOnboarded: false }),
}));
