import React from "react";

const services = [
  { id: "WITHDRAWAL", label: "سحب نقدي" },
  { id: "DEPOSIT", label: "إيداع نقدي" },
  { id: "CURRENCY_EXCHANGE", label: "تحويل عملة" },
  { id: "CHECK_DEPOSIT", label: "إيداع شيك" },
];

export default function ServiceGrid({ selectedService, onSelect }) {
  return (
    <div
      className="svc-grid"
      style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "7px" }}
    >
      {services.map((svc) => (
        <button
          key={svc.id}
          onClick={() => onSelect(svc.id)}
          className={`svc-btn ${selectedService === svc.id ? "active" : ""}`}
          style={{
            border: "1px solid rgba(255,255,255,0.65)",
            borderRadius: "12px",
            padding: "11px 8px",
            fontSize: "11px",
            fontWeight: "600",
            background:
              selectedService === svc.id ? "#101B2D" : "rgba(255,255,255,.45)",
            color: selectedService === svc.id ? "#fff" : "#101B2D",
            textAlign: "center",
            cursor: "pointer",
            transition: "all 0.2s",
            boxShadow:
              selectedService === svc.id
                ? "0 8px 18px -6px rgba(16,27,45,.4)"
                : "none",
          }}
        >
          {svc.label}
        </button>
      ))}
    </div>
  );
}
