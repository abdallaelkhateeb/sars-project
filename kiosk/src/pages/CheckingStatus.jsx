// src/pages/CheckingStatus.jsx
import React from "react";

export default function CheckingStatus() {
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
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: "18px",
        }}
      >
        <div style={{ position: "relative", width: "52px", height: "52px" }}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: "3px solid rgba(34,197,94,0.15)",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              border: "3px solid transparent",
              borderTopColor: "#22C55E",
              animation: "sars-spin 0.9s linear infinite",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%,-50%)",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: "#22C55E",
            }}
          />
        </div>

        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontSize: "13px",
              fontWeight: "700",
              color: "#101B2D",
              marginBottom: "4px",
            }}
          >
            جار التحقق من توفر الخدمة
          </div>
          <div style={{ fontSize: "12px", color: "#57657C" }}>
            على هذه الماكينة...
          </div>
        </div>

        <div style={{ width: "100%", maxWidth: "200px" }}>
          <div
            style={{
              width: "100%",
              height: "5px",
              borderRadius: "3px",
              background: "rgba(139,152,172,0.2)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: "55%",
                height: "100%",
                borderRadius: "3px",
                background: "#22C55E",
                animation: "sars-progress 1.6s ease-in-out infinite",
              }}
            />
          </div>
        </div>
      </div>

      <style>{`
        @keyframes sars-spin { to { transform: rotate(360deg); } }
        @keyframes sars-progress {
          0% { width: 15%; }
          50% { width: 85%; }
          100% { width: 15%; }
        }
      `}</style>
    </div>
  );
}