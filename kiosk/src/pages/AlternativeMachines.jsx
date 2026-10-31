// src/pages/AlternativeMachines.jsx
import React, { useState } from "react";
import { useSessionStore } from "../store/sessionSlice";

export default function AlternativeMachines() {
  const { alternatives, setChosenAtm } = useSessionStore();

  const [selectedId, setSelectedId] = useState(
    alternatives.length > 0 ? alternatives[0].id : null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = () => {
    if (!selectedId) return;
    setIsSubmitting(true);
    setChosenAtm(selectedId);
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
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "14px",
        }}
      >
        <span
          style={{
            fontFamily: '"IBM Plex Mono", monospace',
            fontSize: "10px",
            color: "#8B98AC",
          }}
        >
          10:24
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
          <span
            style={{
              fontSize: "10px",
              fontWeight: "700",
              color: "#101B2D",
              letterSpacing: "1px",
            }}
          >
            SARS
          </span>
          <span
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: "#22C55E",
              display: "inline-block",
            }}
          />
        </div>
      </div>

      <div
        style={{
          fontSize: "15.5px",
          fontWeight: "700",
          color: "#101B2D",
          marginBottom: "12px",
        }}
      >
        اختار الماكينة الأقرب ليك
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          flex: 1,
        }}
      >
        {alternatives.length === 0 && (
          <div
            style={{
              fontSize: "11px",
              color: "#8B98AC",
              textAlign: "center",
              padding: "20px",
            }}
          >
            مفيش ماكينات بديلة متاحة حالياً
          </div>
        )}

        {alternatives.map((atm) => {
          const isSelected = selectedId === atm.id;
          return (
            <button
              key={atm.id}
              onClick={() => setSelectedId(atm.id)}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                textAlign: "right",
                border: isSelected
                  ? "1.5px solid #22C55E"
                  : "1px solid rgba(139,152,172,0.25)",
                background: isSelected
                  ? "rgba(34,197,94,0.06)"
                  : "rgba(255,255,255,0.5)",
                borderRadius: "12px",
                padding: "11px 12px",
                cursor: "pointer",
                width: "100%",
              }}
            >
              <div
                style={{
                  padding: "4px 9px",
                  borderRadius: "8px",
                  border: "1px solid rgba(34,197,94,0.4)",
                  background: "rgba(34,197,94,0.08)",
                  fontSize: "9.5px",
                  fontWeight: "600",
                  color: "#22C55E",
                  whiteSpace: "nowrap",
                }}
              >
                متاح
              </div>
              <div>
                <div
                  style={{
                    fontSize: "12.5px",
                    fontWeight: "700",
                    color: "#101B2D",
                    marginBottom: "3px",
                  }}
                >
                  {atm.branchName}
                </div>
                <div style={{ fontSize: "10px", color: "#8B98AC" }}>
                  {atm.etaMinutes} دقيقة · {atm.distanceKm} km
                </div>
              </div>
            </button>
          );
        })}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!selectedId || isSubmitting}
        style={{
          marginTop: "14px",
          background: "#101B2D",
          color: "#fff",
          padding: "13px",
          borderRadius: "13px",
          border: "none",
          fontSize: "12.5px",
          fontWeight: "600",
          cursor: "pointer",
          opacity: !selectedId || isSubmitting ? 0.6 : 1,
        }}
      >
        {isSubmitting ? "جاري الإرسال..." : "إرسال التفاصيل على الموبايل"}
      </button>
    </div>
  );
}
