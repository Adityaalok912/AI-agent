

// const api = axios.create({
//   baseURL: import.meta.env.VITE_API_URL || "http://localhost:8080/api",
// });

// export default api;
// src/api/client.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8080/api",
  headers: { "Content-Type": "application/json" },
});

export default api;

export async function runWorkflow(title, prompt) {
  try {
    const response = await api.post("/agents/run", { title, prompt });
    return response.data;
  } catch (error) {
    console.error("Error running workflow:", error);
    throw error;
  }
}



