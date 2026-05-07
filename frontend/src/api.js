import axios from "axios";

const API = axios.create({
  baseURL: "https://aiui-generator.onrender.com",
});

export default API;
