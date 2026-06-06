import axios from "axios";

// [중요] 외부 접속(Tunnel) 모드 사용 시:
// 백엔드 터널 주소 적용 (npx localtunnel --port 8000)
const BASE_URL = "https://eight-cobras-yell.loca.lt";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
