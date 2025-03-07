import { useSelector } from "react-redux";

export const useRawMessages = () => {
  const { raw_message, loading, error, total } = useSelector(
    (state) => state.raw_message
  );

  // Ensure raw_message is an array
  const rawMessages = Array.isArray(raw_message)
    ? raw_message
    : raw_message?.data || [];

  return { rawMessages, loading, error, total };
};
