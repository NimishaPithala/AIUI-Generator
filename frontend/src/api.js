import axios from "axios";

// Hardcode your Render backend URL directly here
const API = axios.create({
  baseURL: "https://aiui-generator.onrender.com",
  headers: { "Content-Type": "application/json" },
  timeout: 60000, // 60s — Groq can be slow on free tier
});

export default API;
