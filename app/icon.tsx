import { ImageResponse } from "next/og";

export const size = {
  width: 64,
  height: 64,
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          height: "100%",
          width: "100%",
          alignItems: "center",
          justifyContent: "center",
          background: "#090909",
          borderRadius: 16,
          border: "1px dashed rgba(255,255,255,0.18)",
          color: "#f5f5f5",
          fontFamily: "monospace",
          fontSize: 34,
          fontWeight: 700,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <span>O</span>
          <span style={{ opacity: 0.68 }}>|</span>
        </div>
      </div>
    ),
    size,
  );
}
