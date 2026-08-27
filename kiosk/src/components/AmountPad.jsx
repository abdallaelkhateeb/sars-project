import React from "react";

export default function AmountPad({
  amount,
  setAmount,
  onSubmit,
  isSubmitting,
}) {
  return (
    <div
      className="amount-pad"
      style={{
        marginTop: "auto",
        border: "1px solid rgba(255,255,255,0.65)",
        borderRadius: "16px",
        padding: "12px",
        background: "rgba(255,255,255,.4)",
      }}
    >
      <div
        className="lbl"
        style={{ fontSize: "9.5px", color: "#8B98AC", marginBottom: "4px" }}
      >
        المبلغ المطلوب
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: "5px" }}>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0"
          style={{
            fontFamily: '"IBM Plex Mono", monospace',
            fontSize: "19px",
            fontWeight: "600",
            color: "#101B2D",
            background: "transparent",
            border: "none",
            outline: "none",
            width: "100%",
          }}
        />
        <span style={{ fontSize: "11px", color: "#8B98AC" }}>EGP</span>
      </div>
      <button
        onClick={onSubmit}
        disabled={isSubmitting || !amount}
        className="cta"
        style={{
          marginTop: "10px",
          background: "#101B2D",
          color: "#fff",
          padding: "12px",
          borderRadius: "13px",
          fontSize: "12px",
          fontWeight: "600",
          width: "100%",
          cursor: "pointer",
          border: "none",
        }}
      >
        {isSubmitting ? "جاري المعالجة..." : "متابعة"}
      </button>
    </div>
  );
}
