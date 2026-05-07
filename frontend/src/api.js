import axios from "axios";

const API = axios.create({
  baseURL: "https://YOUR_BACKEND.onrender.com"
});

export default API;