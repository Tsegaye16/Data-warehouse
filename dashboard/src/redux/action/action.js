import { createAsyncThunk } from "@reduxjs/toolkit";
import * as api from "../api/api";

export const getMessage = createAsyncThunk(
  "GET_MESSAGE",
  async ({ page, page_size }, { rejectWithValue }) => {
    try {
      const response = await api.getMessage(page, page_size);
      console.log(response);
      return response; // Return the response data
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);

export const getRawMessage = createAsyncThunk(
  "GET_RAW_MESSAGE",
  async ({ page, page_size }, { rejectWithValue }) => {
    try {
      const response = await api.getRawMessage(page, page_size);
      return response; // Return the response data
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);

export const fetchRecent = createAsyncThunk(
  "FETCH_RECENT",
  async (_, { rejectWithValue }) => {
    try {
      console.log("dud clicked");
      const response = await api.fetchRecent();
      return response; // Return the response data
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);

export const processMessage = createAsyncThunk(
  "PROCESS_MESSAGE",
  async (data, { rejectWithValue }) => {
    try {
      const response = await api.processMessage(data);
      return response; // Return the response data
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || error.message);
    }
  }
);
