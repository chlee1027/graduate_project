import axios from "axios";
import { Platform } from "react-native";

// [중요] 외부 접속(Tunnel) 모드 사용 시:
// 백엔드 터널 주소 적용 (npx localtunnel --port 8000)
// 웹 환경에서는 localhost 서버에 직접 접근하는 것이 가장 빠르고 안전합니다.
const BASE_URL = Platform.OS === "web" ? "http://127.0.0.1:8000" : "https://lovely-ideas-cover.loca.lt";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
    "Bypass-Tunnel-Reminder": "true", // 로컬터널 경고 페이지 우회용 헤더
  },
});

export default client;
