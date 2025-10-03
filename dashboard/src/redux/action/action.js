import { createAsyncThunk } from "@reduxjs/toolkit";
import * as api from "../api/api";

export const getMessage = createAsyncThunk(
  "GET_MESSAGE",
  async (
    { page, page_size, channel_name, start_date, end_date },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.getMessage(
        page,
        page_size,
        channel_name,
        start_date,
        end_date
      );
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);

export const getRawMessage = createAsyncThunk(
  "GET_RAW_MESSAGE",
  async (
    { page, page_size, channel_name, start_date, end_date },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.getRawMessage(
        page,
        page_size,
        channel_name,
        start_date,
        end_date
      );
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);

export const fetchRecent = createAsyncThunk(
  "FETCH_RECENT",
  async (data, { rejectWithValue }) => {
    try {
      console.log("Fetching recent messages...");
      const response = await api.fetchRecent(data);
      console.log("Fetch response:", response);
      return response;
    } catch (error) {
      console.error("Fetch error:", error);
      return rejectWithValue(
        error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message
      );
    }
  }
);

export const processMessage = createAsyncThunk(
  "PROCESS_MESSAGE",
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.processMessage(data);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);
