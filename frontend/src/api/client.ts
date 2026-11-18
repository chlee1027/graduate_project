import axios from "axios";
import { Platform } from "react-native";

// API 주소 정하는 순서
// 1. EXPO_PUBLIC_API_URL 이 있으면 그 주소 (빌드할 때 박힌다)
// 2. 웹 개발 서버(expo start --web)면 로컬 백엔드 http://127.0.0.1:8000
// 3. 웹 배포 빌드면 같은 주소의 /api (Vercel 이 프런트와 백엔드를 한 주소로 낸다)
// 4. 기기(Expo Go)면 터널 주소. 시연 때 npx localtunnel --port 8000 으로 받은 주소로 바꾼다.
const TUNNEL_URL = "https://lovely-ideas-cover.loca.lt";

function resolveBaseUrl(): string {
  const fromEnv = process.env.EXPO_PUBLIC_API_URL;
  if (fromEnv) return fromEnv;
  if (Platform.OS === "web") return __DEV__ ? "http://127.0.0.1:8000" : "";
  return TUNNEL_URL;
}

const BASE_URL = resolveBaseUrl();

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
    "Bypass-Tunnel-Reminder": "true", // 로컬터널 경고 페이지 우회용 헤더
  },
});

export default client;
