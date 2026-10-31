// src/pages/MachineUnavailable.jsx
import React from "react";
import { useSessionStore } from "../store/sessionSlice";

// كل سبب ليه نص ووصف مختلف حسب الملاحظة في التصميم
const REASONS = {
  INSUFFICIENT_CASH: {
    title: "الماكينة دي مش متاحة دلوقتي",
    desc: "رصيد الكاش الحالي مش كافي لمبلغ السحب اللي طلبته. متقلقش، فلوسك في أمان — هنوجهك لأقرب ماكينة تقدر تخدمك حالاً.",
  },
  OFFLINE: {
    title: "الماكينة دي مش شغالة دلوقتي",
    desc: "في عطل مؤقت في الاتصال بالماكينة. هنوجهك لأقرب ماكينة تانية شغالة.",
  },
  MAINTENANCE: {
    title: "الماكينة دي تحت الصيانة حالياً",
    desc: "فريقنا بيصلح الماكينة دي دلوقتي. هنوجهك لأقرب ماكينة بديلة.",
  },
  NO_CASH: {
    title: "الماكينة دي من غير رصيد كاش",
    desc: "الماكينة خلصت رصيدها النقدي. هنوجهك لأقرب ماكينة فيها كاش كافي.",
  },
};

export default function MachineUnavailable() {
  const { redirectReason, alternatives, setStep, resetSession } =
    useSessionStore();

  // const reason = REASONS[ redirectReason ] || REASONS.OFFLINE;
  const reason = REASONS[redirectReason];

  const altCount = alternatives?.length || 5;

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
          width: "44px",
          height: "44px",
          borderRadius: "13px",
          background: "#FEE2E2",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: "12px",
        }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <rect
            x="2"
            y="6"
            width="20"
            height="13"
            rx="2.5"
            stroke="#EF4444"
            strokeWidth="1.8"
          />
          <line
            x1="2"
            y1="10.5"
            x2="22"
            y2="10.5"
            stroke="#EF4444"
            strokeWidth="1.8"
          />
          <line
            x1="3"
            y1="3"
            x2="21"
            y2="21"
            stroke="#EF4444"
            strokeWidth="1.8"
          />
        </svg>
      </div>

      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "5px",
          background: "rgba(239,68,68,0.08)",
          border: "1px solid rgba(239,68,68,0.25)",
          borderRadius: "8px",
          padding: "4px 8px",
          marginBottom: "10px",
          width: "fit-content",
        }}
      >
        <span
          style={{
            fontFamily: '"IBM Plex Mono", monospace',
            fontSize: "9.5px",
            color: "#EF4444",
            fontWeight: "600",
          }}
        >
          reason: {redirectReason || "OFFLINE"}
        </span>
        <span
          style={{
            width: "5px",
            height: "5px",
            borderRadius: "50%",
            background: "#EF4444",
          }}
        />
      </div>

      <div
        style={{
          fontSize: "15px",
          fontWeight: "700",
          color: "#101B2D",
          marginBottom: "6px",
        }}
      >
        {reason.title}
      </div>
      <div
        style={{
          fontSize: "11.5px",
          color: "#57657C",
          lineHeight: "1.6",
          marginBottom: "14px",
        }}
      >
        {reason.desc}
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "11px",
          color: "#101B2D",
          fontWeight: "600",
          background: "rgba(16,27,45,0.05)",
          borderRadius: "10px",
          padding: "10px",
          marginBottom: "auto",
        }}
      >
        <span
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: "#22C55E",
            flexShrink: 0,
          }}
        />
        بنجهزلك أقرب {altCount} بدائل الآن
        <span style={{ fontWeight: "400", color: "#57657C" }}>
          حسب موقعك ونوع الخدمة المطلوبة
        </span>
      </div>

      <button
        onClick={() => setStep(4)}
        style={{
          marginTop: "12px",
          background: "#101B2D",
          color: "#fff",
          padding: "13px",
          borderRadius: "13px",
          border: "none",
          fontSize: "12.5px",
          fontWeight: "600",
          cursor: "pointer",
        }}
      >
        عرض الماكينات البديلة
      </button>
      <button
        onClick={resetSession}
        style={{
          marginTop: "8px",
          background: "transparent",
          color: "#101B2D",
          padding: "13px",
          borderRadius: "13px",
          border: "1px solid rgba(16,27,45,0.15)",
          fontSize: "12.5px",
          fontWeight: "600",
          cursor: "pointer",
        }}
      >
        إلغاء العملية
      </button>
    </div>
  );
}
