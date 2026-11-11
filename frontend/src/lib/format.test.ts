import { describe, expect, it } from "vitest";

import { describeDetail } from "./api";
import { formatKm, labelFor, localMonth, localToday, monthToPeriod } from "./format";

describe("describeDetail", () => {
  it("devuelve el texto cuando el detalle es una cadena", () => {
    expect(describeDetail("Ruta no encontrada", "x")).toBe("Ruta no encontrada");
  });

  it("une los errores de validación con el nombre del campo", () => {
    const detail = [
      { loc: ["body", "stops"], msg: "List should have at least 2 items" },
      { loc: ["body", "departure_date"], msg: "Field required" },
    ];

    expect(describeDetail(detail, "x")).toBe(
      "stops: List should have at least 2 items; departure_date: Field required",
    );
  });

  it("usa el texto de respaldo cuando no hay detalle utilizable", () => {
    expect(describeDetail(undefined, "Revisa los datos")).toBe("Revisa los datos");
    expect(describeDetail("   ", "Revisa los datos")).toBe("Revisa los datos");
    expect(describeDetail([], "Revisa los datos")).toBe("Revisa los datos");
  });
});

describe("formato", () => {
  it("muestra la distancia o su ausencia", () => {
    expect(formatKm(null)).toBe("Sin distancia");
    expect(formatKm(12.34)).toBe("12,3 km");
  });

  it("traduce códigos conocidos y humaniza los desconocidos", () => {
    expect(labelFor("furgon_refrigerado")).toBe("Furgón refrigerado");
    expect(labelFor("camion_cisterna")).toBe("Camion cisterna");
  });

  it("convierte un mes en el primer día del período", () => {
    expect(monthToPeriod("2026-03")).toBe("2026-03-01");
  });

  it("usa la fecha local y no la UTC para los valores por defecto", () => {
    // 30 de noviembre a las 23:30 hora local: en UTC-5 ya es 1 de diciembre.
    const lateEvening = new Date(2026, 10, 30, 23, 30);

    expect(localToday(lateEvening)).toBe("2026-11-30");
    expect(localMonth(lateEvening)).toBe("2026-11");
  });
});
