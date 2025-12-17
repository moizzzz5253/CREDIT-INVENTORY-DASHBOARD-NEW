import api from "./axios";

export const createBorrow = async (payload) => {
  const res = await api.post("/borrow/", payload);
  return res.data;
};

export const getActiveBorrowers = async () => {
  const res = await api.get("/borrow/active");
  return res.data;
};
