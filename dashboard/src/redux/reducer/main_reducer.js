import { combineReducers } from "@reduxjs/toolkit";
import messageReducer from "./message_reducer";
import raw_messageReducer from "./raw_message_reducer";

const appReducer = combineReducers({
  message: messageReducer,
  raw_message: raw_messageReducer,
});

export default appReducer;
