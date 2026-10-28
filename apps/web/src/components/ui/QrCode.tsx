import { useMemo } from "react";
import { encode } from "uqr";

/**
 * QR code drawn as one SVG path (no canvas, no HTML injection). Always dark on
 * white, whatever the theme, because phone scanners expect that contrast. Level L
 * error correction keeps the long wa.me link at a size phone cameras read easily.
 */
export function QrCode({
  value,
  label,
  size = 232,
}: {
  value: string;
  label: string;
  size?: number;
}) {
  const { path, modules } = useMemo(() => {
    const { data, size: count } = encode(value, { ecc: "L", border: 2 });
    let d = "";
    data.forEach((row, y) => {
      row.forEach((dark, x) => {
        if (dark) d += `M${x} ${y}h1v1h-1z`;
      });
    });
    return { path: d, modules: count };
  }, [value]);

  return (
    <svg
      role="img"
      aria-label={label}
      width={size}
      height={size}
      viewBox={`0 0 ${modules} ${modules}`}
      shapeRendering="crispEdges"
      className="bg-white"
    >
      <rect width={modules} height={modules} fill="#fff" />
      <path d={path} fill="#16130f" />
    </svg>
  );
}
