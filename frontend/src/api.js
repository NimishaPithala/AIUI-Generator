import axios from "axios";

// Hardcode your Render backend URL directly here
const API = axios.create({
  baseURL: "https://aiui-generator.onrender.com",
  headers: { "Content-Type": "application/json" },
  timeout: 900000, // for deepseek to render to frontend
});

export default API;
