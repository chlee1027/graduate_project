import axios from "axios";

// Update this to your local IP if testing on a real device via Expo Go
// Example: "http://192.168.1.5:8000"
const BASE_URL = "http://YOUR_LOCAL_IP:8000";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default client;
