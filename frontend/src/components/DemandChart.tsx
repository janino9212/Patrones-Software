import { formatMonth, formatNumber } from "../lib/format";
import type { DemandRecord } from "../lib/types";

interface ForecastPoint {
  value: number;
  low: number;
  high: number;
}

interface DemandChartProps {
  records: DemandRecord[];
  forecast: ForecastPoint | null;
}

const HEIGHT = 190;
const TOP = 24;
const BOTTOM = 30;
const SLOT = 64;
const BAR = 38;

/** Demanda real por período (barras) y, al final, el pronóstico del
 *  siguiente período con su intervalo de confianza. */
export function DemandChart({ records, forecast }: DemandChartProps) {
  const slots = records.length + (forecast ? 1 : 0);
  const width = Math.max(slots * SLOT, SLOT * 4);
  const peak = Math.max(...records.map((record) => record.quantity), forecast?.high ?? 0, 1);
  const plot = HEIGHT - TOP - BOTTOM;
  const y = (value: number): number => TOP + plot - (value / peak) * plot;
  const baseline = TOP + plot;

  const summary = [
    ...records.map((record) => `${formatMonth(record.period)}: ${formatNumber(record.quantity)}`),
    forecast ? `Pronóstico: ${formatNumber(forecast.value)}` : "",
  ]
    .filter(Boolean)
    .join(", ");

  return (
    <div className="overflow-x-auto">
      <svg
        viewBox={`0 0 ${width} ${HEIGHT}`}
        style={{ minWidth: Math.min(width, 520), width: "100%", maxHeight: 230 }}
        role="img"
        aria-label={`Demanda por período. ${summary}`}
      >
        <line x1="0" x2={width} y1={baseline} y2={baseline} className="stroke-line-strong" />
        {records.map((record, index) => {
          const x = index * SLOT + (SLOT - BAR) / 2;
          return (
            <g key={record.period}>
              <rect
                x={x}
                y={y(record.quantity)}
                width={BAR}
                height={Math.max(baseline - y(record.quantity), 1)}
                rx="3"
                className="fill-rail"
              />
              <text
                x={x + BAR / 2}
                y={y(record.quantity) - 6}
                textAnchor="middle"
                className="num fill-ink text-[11px] font-semibold"
              >
                {formatNumber(record.quantity)}
              </text>
              <text
                x={x + BAR / 2}
                y={HEIGHT - 10}
                textAnchor="middle"
                className="fill-ink-soft text-[11px]"
              >
                {formatMonth(record.period)}
              </text>
            </g>
          );
        })}
        {forecast &&
          (() => {
            const x = records.length * SLOT + (SLOT - BAR) / 2;
            const center = x + BAR / 2;
            return (
              <g>
                <rect
                  x={x}
                  y={y(forecast.value)}
                  width={BAR}
                  height={Math.max(baseline - y(forecast.value), 1)}
                  rx="3"
                  className="fill-signal stroke-ink"
                  strokeWidth="1.5"
                  strokeDasharray="4 3"
                />
                <line
                  x1={center}
                  x2={center}
                  y1={y(forecast.high)}
                  y2={y(forecast.low)}
                  className="stroke-ink"
                  strokeWidth="1.5"
                />
                <line
                  x1={center - 7}
                  x2={center + 7}
                  y1={y(forecast.high)}
                  y2={y(forecast.high)}
                  className="stroke-ink"
                  strokeWidth="1.5"
                />
                <line
                  x1={center - 7}
                  x2={center + 7}
                  y1={y(forecast.low)}
                  y2={y(forecast.low)}
                  className="stroke-ink"
                  strokeWidth="1.5"
                />
                <text
                  x={center}
                  y={y(forecast.high) - 6}
                  textAnchor="middle"
                  className="num fill-ink text-[11px] font-bold"
                >
                  {formatNumber(forecast.value)}
                </text>
                <text
                  x={center}
                  y={HEIGHT - 10}
                  textAnchor="middle"
                  className="fill-ink text-[11px] font-semibold"
                >
                  Pronóstico
                </text>
              </g>
            );
          })()}
      </svg>
    </div>
  );
}
