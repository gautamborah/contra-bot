import axios from "axios";

const API_URL = "http://localhost:8000"; // FastAPI backend

export const sayHello = async () => {
  try {
    const res = await axios.get(`${API_URL}/hello`);
    return res.data.message;
  } catch (err) {
    console.error("API error:", err);
    return "Error connecting to backend ❌";
  }
};
