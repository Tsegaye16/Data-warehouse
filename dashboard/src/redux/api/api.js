import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const getMessage = async (page, page_size) => {
  try {
    const response = await API.get(`/messages`, {
      params: { page, page_size },
    });
    return response.data; // Return the response data
  } catch (error) {
    throw new Error(
      error.response?.data?.message || "Failed to fetch messages"
    );
  }
};

export const getRawMessage = async (page, page_size) => {
  try {
    const response = await API.get(`/messages/raw`, {
      params: { page, page_size },
    });
    console.log(response);
    return response.data; // Return the response data
  } catch (error) {
    throw new Error(
      error.response?.data?.message || "Failed to fetch raw messages"
    );
  }
};

export const fetchRecent = async () => {
  try {
    const response = await API.post("/messages/recent");
    return response.data; // Return the response data
  } catch (error) {
    throw new Error(
      error.response?.data?.message || "Failed to fetch recent messages"
    );
  }
};
