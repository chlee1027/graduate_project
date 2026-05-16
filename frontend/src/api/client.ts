import axios from "axios";

// Update this to your local IP if testing on a real device via Expo Go
// Your current detected IP: 192.168.45.241
const BASE_URL = "http://192.168.45.241:8000";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
