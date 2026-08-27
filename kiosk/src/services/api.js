import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": import.meta.env.VITE_ATM_API_KEY,
  },
});

const atmId = import.meta.env.VITE_ATM_ID;

export const attemptTransaction = async (requestedService, requestedAmount) => {
  const payload = { requestedService };
  if (requestedAmount) {
    payload.requestedAmount = requestedAmount;
  }
  const response = await api.post(
    `/atms/${atmId}/transactions/attempt`,
    payload,
  );
  return response.data;
};

export const getAlternatives = async (
  requestedService,
  requestedAmount,
  lat,
  lng,
) => {
  const response = await api.post("/routing/alternatives", {
    originAtmId: atmId,
    requestedService,
    requestedAmount,
    lat,
    lng,
  });
  return response.data;
};

export const requestSms = async (
  phoneNumber,
  chosenAtmId,
  requestedService,
) => {
  const response = await api.post("/notifications/sms", {
    phoneNumber,
    chosenAtmId,
    requestedService,
  });
  return response.data;
};

export default api;
