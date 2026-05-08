import axios from "axios";

// Hardcode your Render backend URL directly here
const API = axios.create({
  baseURL: "https://aiui-generator.onrender.com",
  headers: { "Content-Type": "application/json" },
  timeout: 120000, // 120 seconds — Groq + repair loop can take ~90s on a cold Render start
});

export default API;
