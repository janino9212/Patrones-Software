import { ArrowRight } from "lucide-react";
import { useEffect } from "react";
import { Link, useLocation } from "react-router";

import { PageHeader } from "../components/Shell";
import { Badge } from "../components/ui";
import { PATTERN_CATEGORIES, PATTERNS, patternSlug } from "../data/patterns";
import type { PatternEntry, PatternStatus } from "../data/patterns";

const STATUS: Record<PatternStatus, { label: string; tone: "go" | "caution" | "idle" }> = {
  implementado: { label: "Implementado", tone: "go" },
  limitado: { label: "Aplicabilidad limitada", tone: "caution" },
  descartado: { label: "No aplica", tone: "idle" },
};

function PatternRow({ pattern, highlighted }: { pattern: PatternEntry; highlighted: boolean }) {
  const status = STATUS[pattern.status];
  return (
    <li
      id={patternSlug(pattern.name)}
      className={`scroll-mt-6 grid gap-x-6 gap-y-1.5 px-5 py-4 transition-colors duration-500 md:grid-cols-[13rem_1fr] ${
        highlighted ? "bg-signal-soft" : ""
      }`}
    >
      <div>
        <h3 className="text-[1.05rem] font-bold">{pattern.name}</h3>
        <p className="mt-1">
          <Badge tone={status.tone}>{status.label}</Badge>
        </p>
      </div>
      <div className="min-w-0">
        <p className="max-w-[70ch]">{pattern.reason}</p>
        {pattern.source && (
          <p className="mt-1.5 flex flex-wrap gap-x-3 text-[0.8rem] text-ink-soft">
            <span className="font-semibold">Módulo {pattern.module}</span>
            <span className="num min-w-0 break-words">{pattern.source}</span>
          </p>
        )}
        {pattern.screen && pattern.screen.path !== "/login" && (
          <Link
            to={pattern.screen.path}
            className="mt-1.5 inline-flex items-center gap-1 text-[0.9rem] font-semibold text-info"
          >
            Verlo en {pattern.screen.label}
            <ArrowRight className="size-4" aria-hidden />
          </Link>
        )}
      </div>
    </li>
  );
}

export function PatternsPage() {
  const { hash } = useLocation();
  const target = hash.replace("#", "");

  useEffect(() => {
    if (!target) return;
    document.getElementById(target)?.scrollIntoView({ block: "center" });
  }, [target]);

  const implemented = PATTERNS.filter((pattern) => pattern.status !== "descartado").length;

  return (
    <>
      <PageHeader title="Patrones de diseño">
        De los 23 patrones del catálogo GoF, el sistema aplica {implemented}. Los{" "}
        {PATTERNS.length - implemented} restantes no resuelven ningún problema real aquí, y se
        explica por qué.
      </PageHeader>

      <div className="space-y-5">
        {PATTERN_CATEGORIES.map((category) => {
          const entries = PATTERNS.filter((pattern) => pattern.category === category);
          const applied = entries.filter((pattern) => pattern.status !== "descartado").length;
          return (
            <section key={category} className="rounded-panel border border-line bg-surface">
              <header className="flex items-baseline gap-3 border-b border-line px-5 py-3">
                <h2 className="text-[1.15rem] font-bold">
                  {category === "Comportamiento" ? "De comportamiento" : `${category}es`}
                </h2>
                <p className="num text-[0.88rem] text-ink-soft">
                  {applied} de {entries.length} aplicados
                </p>
              </header>
              <ul className="divide-y divide-line">
                {entries.map((pattern) => (
                  <PatternRow
                    key={pattern.name}
                    pattern={pattern}
                    highlighted={patternSlug(pattern.name) === target}
                  />
                ))}
              </ul>
            </section>
          );
        })}
      </div>
    </>
  );
}
