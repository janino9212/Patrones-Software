import type { StripStop } from "../components/StripMap";

export interface Stage {
  code: string;
  label: string;
}

/** Recorrido de un producto, del fabricante al cliente final. */
export const STAGES: readonly Stage[] = [
  { code: "fabricacion", label: "Fabricación" },
  { code: "almacenamiento", label: "Almacenamiento" },
  { code: "transporte", label: "Transporte" },
  { code: "distribucion", label: "Distribución" },
  { code: "entrega", label: "Entrega" },
];

export function stageLabel(code: string): string {
  return STAGES.find((stage) => stage.code === code)?.label ?? code;
}

/** Convierte la etapa actual en las paradas del mapa de línea. */
export function stageStops(currentStage: string | null): StripStop[] {
  const currentIndex = STAGES.findIndex((stage) => stage.code === currentStage);
  return STAGES.map((stage, index) => ({
    label: stage.label,
    state:
      currentIndex === -1 || index > currentIndex
        ? "pending"
        : index === currentIndex
          ? "current"
          : "done",
  }));
}
