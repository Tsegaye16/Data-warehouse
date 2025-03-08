import { createSlice } from "@reduxjs/toolkit";
import { getRawMessage, fetchRecent, processMessage } from "../action/action";

const initialState = {
  raw_message: [],
  loading: false,
  error: null,
  total: 0, // Added total for pagination
};

const raw_messageSlice = createSlice({
  name: "raw_message",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getRawMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getRawMessage.fulfilled, (state, action) => {
        state.loading = false;
        console.log(action.payload);
        state.raw_message = action.payload.messages; // Update messages
        state.total = action.payload.total; // Update total count
      })
      .addCase(getRawMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload; // Set error message
      })
      .addCase(fetchRecent.pending, (state, action) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecent.fulfilled, (state, action) => {
        state.loading = false;
        console.log(action);
        state.raw_message = action.payload.messages;
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
        state.raw_message = []; // Clear the state after processing
        state.total = 0;
      })
      .addCase(processMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export default raw_messageSlice.reducer;
