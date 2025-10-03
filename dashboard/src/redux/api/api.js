import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Add response interceptor for better error handling
API.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const getMessage = async (
  page,
  page_size,
  channel_name,
  start_date,
  end_date
) => {
  try {
    const response = await API.get(`/messages`, {
      params: { page, page_size, channel_name, start_date, end_date },
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail ||
        error.response?.data?.message ||
        "Failed to fetch messages"
    );
  }
};

export const getRawMessage = async (
  page,
  page_size,
  channel_name,
  start_date,
  end_date
) => {
  try {
    const response = await API.get(`/messages/raw`, {
      params: { page, page_size, channel_name, start_date, end_date },
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail ||
        error.response?.data?.message ||
        "Failed to fetch raw messages"
    );
  }
};

export const fetchRecent = async (data) => {
  try {
    const response = await API.post("/messages/recent", data);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail ||
        error.response?.data?.message ||
        "Failed to fetch recent messages"
    );
  }
};

export const processMessage = async (data) => {
  try {
    const response = await API.post("/messages/process", data);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail ||
        error.response?.data?.message ||
        "Failed to process messages"
    );
  }
};
