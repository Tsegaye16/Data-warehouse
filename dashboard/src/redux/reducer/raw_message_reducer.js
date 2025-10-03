import { createSlice } from "@reduxjs/toolkit";
import { getRawMessage, fetchRecent, processMessage } from "../action/action";

const initialState = {
  raw_message: [],
  loading: false,
  error: null,
  total: 0,
};

const raw_messageSlice = createSlice({
  name: "raw_message",
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getRawMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getRawMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.raw_message = action.payload.messages || [];
        state.total = action.payload.total || 0;
      })
      .addCase(getRawMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(fetchRecent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecent.fulfilled, (state, action) => {
        state.loading = false;
        // The fetched messages should now be in the database,
        // so we don't need to update the state directly
        // The getRawMessage call will refresh the data
        console.log("Fetch recent successful:", action.payload);
      })
      .addCase(fetchRecent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(processMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(processMessage.fulfilled, (state) => {
        state.loading = false;
        state.raw_message = [];
        state.total = 0;
      })
      .addCase(processMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = raw_messageSlice.actions;
export default raw_messageSlice.reducer;
