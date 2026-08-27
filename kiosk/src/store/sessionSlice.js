import { create } from "zustand";

const initialState = {
  step: 1, // 1: SelectService, 2: Checking, 3: Unavailable, 4: Alternatives, 5: Phone, 6: Confirm
  requestedService: null,
  requestedAmount: null,
  redirectReason: null,
  alternatives: [],
  chosenAtmId: null,
  phoneNumber: null,
};

export const useSessionStore = create((set) => ({
  ...initialState,

  setStep: (step) => set({ step }),

  setRequestDetails: (service, amount) =>
    set({
      requestedService: service,
      requestedAmount: amount,
      step: 2,
    }),

  setRedirect: (reason, alternatives) =>
    set({
      redirectReason: reason,
      alternatives: alternatives,
      step: 3,
    }),

  setChosenAtm: (atmId) =>
    set({
      chosenAtmId: atmId,
      step: 5,
    }),

  setPhoneNumber: (phone) => set({ phoneNumber: phone }),

  resetSession: () => set(initialState),
}));
