import { createSlice } from "@reduxjs/toolkit";
import { getMessage } from "../action/action";

const initialState = {
  messages: [],
  loading: false,
  error: null,
  total: 0, // Added total for pagination
};

const messageSlice = createSlice({
  name: "messages",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages = action.payload.messages; // Update messages
        state.total = action.payload.total; // Update total count
      })
      .addCase(getMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload; // Set error message
      });
  },
});

export default messageSlice.reducer;
