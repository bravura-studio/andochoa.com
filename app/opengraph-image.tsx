import { ImageResponse } from "next/og";

export const alt = "ANDOCHOA terminal workspace";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          height: "100%",
          width: "100%",
          background: "#090909",
          color: "#f5f5f5",
          fontFamily: "monospace",
          padding: "44px",
        }}
      >
        <div
          style={{
            display: "flex",
            flex: 1,
            flexDirection: "column",
            border: "1px dashed rgba(255,255,255,0.18)",
            borderRadius: "34px",
            background: "rgba(255,255,255,0.04)",
            overflow: "hidden",
            boxShadow: "0 24px 60px rgba(0,0,0,0.45)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "22px 28px",
              borderBottom: "1px dashed rgba(255,255,255,0.12)",
              background: "rgba(0,0,0,0.42)",
              textTransform: "uppercase",
              letterSpacing: "0.28em",
              fontSize: 20,
              color: "rgba(255,255,255,0.48)",
            }}
          >
            <div style={{ display: "flex", gap: 10 }}>
              <div style={{ width: 14, height: 14, borderRadius: 999, background: "rgba(255,255,255,0.84)" }} />
              <div style={{ width: 14, height: 14, borderRadius: 999, background: "rgba(255,255,255,0.34)" }} />
              <div style={{ width: 14, height: 14, borderRadius: 999, background: "rgba(255,255,255,0.18)" }} />
            </div>
            <div>ANDOCHOA</div>
            <div>~/workspace</div>
          </div>

          <div
            style={{
              display: "flex",
              flex: 1,
              flexDirection: "column",
              justifyContent: "space-between",
              padding: "48px 52px",
              background:
                "radial-gradient(circle at top left, rgba(255,255,255,0.08), transparent 28%), linear-gradient(180deg, rgba(255,255,255,0.04), transparent 24%)",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div
                style={{
                  textTransform: "uppercase",
                  letterSpacing: "0.34em",
                  fontSize: 22,
                  color: "rgba(255,255,255,0.42)",
                }}
              >
                founder terminal
              </div>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  fontSize: 78,
                  fontWeight: 700,
                  letterSpacing: "-0.06em",
                  lineHeight: 1.05,
                }}
              >
                <span>Build in public.</span>
                <span>Keep the shell clean.</span>
              </div>
              <div style={{ maxWidth: 760, fontSize: 30, lineHeight: 1.5, color: "rgba(255,255,255,0.62)" }}>
                Notes, systems, and experiments from Andre Ochoa across products, writing, and BUILD.FUN.FREE.
              </div>
            </div>

            <div
              style={{
                display: "flex",
                gap: 14,
                flexWrap: "wrap",
                fontSize: 24,
                color: "rgba(255,255,255,0.86)",
              }}
            >
              {["/posts", "/vault", "/about"].map((item) => (
                <div
                  key={item}
                  style={{
                    border: "1px dashed rgba(255,255,255,0.16)",
                    borderRadius: 999,
                    padding: "12px 20px",
                    background: "rgba(255,255,255,0.04)",
                  }}
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    ),
    size,
  );
}
