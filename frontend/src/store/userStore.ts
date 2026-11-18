import { Platform } from "react-native";
import { create } from "zustand";

interface UserState {
  userId: string | null;
  username: string | null;
  token: string | null;
  isOnboarded: boolean;
  setSession: (s: { userId: string; username: string; token: string }) => void;
  reset: () => void;
}

// 로그인 상태(토큰)를 웹은 localStorage 에 둬서 새로고침해도 남게 한다. 기기 앱은 메모리에만 둔다.
// 같은 계정으로 다른 기기에서 로그인하면 서버의 기록을 그대로 이어서 쓴다.
// zustand/middleware 의 persist 는 import.meta 를 써서 Expo 웹 번들에서 깨지므로 직접 쓴다.
const KEY = "fitness-ai-user";
const storage = Platform.OS === "web" && typeof window !== "undefined" ? window.localStorage : null;
const EMPTY = { userId: null, username: null, token: null, isOnboarded: false };

function load() {
  try {
    const saved = storage?.getItem(KEY);
    if (saved) {
      const v = JSON.parse(saved);
      // 토큰이 없는 예전 저장값은 로그인 안 한 것으로 본다
      if (v.token && v.userId) return { userId: v.userId, username: v.username ?? null, token: v.token, isOnboarded: true };
    }
  } catch {
    // 저장값이 깨졌으면 처음 상태로 시작한다
  }
  return EMPTY;
}

export const useUserStore = create<UserState>((set) => ({
  ...load(),
  setSession: ({ userId, username, token }) => set({ userId, username, token, isOnboarded: true }),
  reset: () => set(EMPTY),
}));

useUserStore.subscribe((s) => {
  try {
    if (s.token) storage?.setItem(KEY, JSON.stringify({ userId: s.userId, username: s.username, token: s.token }));
    else storage?.removeItem(KEY);
  } catch {
    // 저장소를 쓸 수 없는 환경(사생활 보호 모드 등)에서는 메모리로만 쓴다
  }
});
