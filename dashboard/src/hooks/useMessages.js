import { useSelector } from "react-redux";

export const useMessages = () => {
  const { messages, loading, error, total } = useSelector(
    (state) => state.message
  );
  return { messages, loading, error, total };
};
