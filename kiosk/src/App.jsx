import React from "react";
import { useSessionStore } from "./store/sessionSlice";
import SelectService from "./pages/SelectService";

function App() {
  const step = useSessionStore((state) => state.step);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#0B1120",
        fontFamily: "sans-serif",
      }}
    >
      <div style={{ width: "100%", maxWidth: "400px" }}>
        {step === 1 && <SelectService />}

        {step === 2 && (
          <div style={{ color: "white", textAlign: "center", padding: "20px" }}>
            جاري التحقق من حالة الماكينة... (شاشة صفية)
          </div>
        )}
        {step === 3 && (
          <div style={{ color: "white", textAlign: "center", padding: "20px" }}>
            الخدمة غير متاحة مؤقتاً (شاشة صفية)
          </div>
        )}
        {step > 3 && (
          <div style={{ color: "white", textAlign: "center", padding: "20px" }}>
            باقي الخطوات...
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
