import { Platform } from "react-native";
import { create } from "zustand";

interface UserState {
  userId: string | null;
  isOnboarded: boolean;
  setUserId: (id: string) => void;
  setIsOnboarded: (status: boolean) => void;
  reset: () => void;
}

// 웹은 새로고침해도 로그인이 남도록 localStorage 에 둔다. 기기 앱은 지금처럼 메모리에만 둔다.
// zustand/middleware 의 persist 는 import.meta 를 써서 Expo 웹 번들에서 깨지므로 직접 쓴다.
const KEY = "fitness-ai-user";
const storage = Platform.OS === "web" && typeof window !== "undefined" ? window.localStorage : null;

function load(): Pick<UserState, "userId" | "isOnboarded"> {
  try {
    const saved = storage?.getItem(KEY);
    if (saved) {
      const v = JSON.parse(saved);
      return { userId: v.userId ?? null, isOnboarded: !!v.isOnboarded };
    }
  } catch {
    // 저장값이 깨졌으면 처음 상태로 시작한다
  }
  return { userId: null, isOnboarded: false };
}

export const useUserStore = create<UserState>((set) => ({
  ...load(),
  setUserId: (id) => set({ userId: id }),
  setIsOnboarded: (status) => set({ isOnboarded: status }),
  reset: () => set({ userId: null, isOnboarded: false }),
}));

useUserStore.subscribe((s) => {
  try {
    storage?.setItem(KEY, JSON.stringify({ userId: s.userId, isOnboarded: s.isOnboarded }));
  } catch {
    // 저장소를 쓸 수 없는 환경(사생활 보호 모드 등)에서는 메모리로만 쓴다
  }
});
