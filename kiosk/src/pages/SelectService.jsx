import React, { useState } from "react";
import { useSessionStore } from "../store/sessionSlice";
import { attemptTransaction } from "../services/api";
import ServiceGrid from "../components/ServiceGrid";
import AmountPad from "../components/AmountPad";

export default function SelectService() {
  const [selectedService, setSelectedService] = useState("WITHDRAWAL");
  const [amount, setAmount] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // استدعاء الدوال من الـ Zustand Store
  const { setRequestDetails, setRedirect } = useSessionStore();

  const handleSubmit = async () => {
    setIsSubmitting(true);
    // نقل الـ state لشاشة التحميل (SCR-02) فوراً عشان نحقق الـ NFR الخاص بالـ 3 ثواني
    setRequestDetails(selectedService, Number(amount));

    try {
      const response = await attemptTransaction(
        selectedService,
        Number(amount),
      );

      if (response.outcome === "REDIRECT") {
        // لو الماكينة فيها مشكلة، ننقله لشاشة SCR-03
        setRedirect(response.reason, response.alternatives);
      } else {
        // لو الماكينة شغالة، يكمل الفلو البنكي الطبيعي (خارج نطاق نظامنا)
        alert("تمت الموافقة! جاري التنفيذ...");
        setIsSubmitting(false);
      }
    } catch (error) {
      console.error("Transaction failed:", error);
      // في حالة فشل الاتصال بالسيرفر
      setRedirect("OFFLINE", []);
    }
  };

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.72)",
        padding: "14px",
        borderRadius: "14px",
        minHeight: "400px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          fontSize: "12px",
          fontWeight: "bold",
          marginBottom: "10px",
          color: "#101B2D",
        }}
      >
        SARS · فرع المهندسين
      </div>
      <div style={{ fontSize: "15.5px", fontWeight: "700", color: "#101B2D" }}>
        اختار الخدمة
      </div>
      <div style={{ fontSize: "11px", color: "#57657C", marginBottom: "14px" }}>
        من فضلك اختار نوع العملية اللي عايز تعملها
      </div>

      <ServiceGrid
        selectedService={selectedService}
        onSelect={setSelectedService}
      />

      {selectedService === "WITHDRAWAL" ? (
        <AmountPad
          amount={amount}
          setAmount={setAmount}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
        />
      ) : (
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          style={{
            marginTop: "auto",
            background: "#101B2D",
            color: "#fff",
            padding: "12px",
            borderRadius: "13px",
            border: "none",
            fontWeight: "600",
            cursor: "pointer",
          }}
        >
          {isSubmitting ? "جاري المعالجة..." : "متابعة"}
        </button>
      )}
    </div>
  );
}
