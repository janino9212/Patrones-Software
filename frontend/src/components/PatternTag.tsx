import { Link } from "react-router";

import { patternSlug } from "../data/patterns";

/** Etiqueta discreta con el patrón GoF que respalda una sección.
 *  Usa el azul de las señales informativas y enlaza al mapa de patrones. */
export function PatternTag({ name }: { name: string }) {
  return (
    <Link
      to={`/patrones#${patternSlug(name)}`}
      title={`Ver dónde se aplica ${name}`}
      className="inline-flex items-center gap-1 rounded-[5px] border border-info/35 bg-info-soft px-1.5 py-0.5 text-[0.74rem] leading-tight font-semibold text-info no-underline transition-colors duration-150 hover:border-info hover:bg-info hover:text-white"
    >
      <svg viewBox="0 0 10 12" className="h-2.5 w-2 shrink-0" aria-hidden>
        {/* Escudo de ruta, como los marcadores de carretera. */}
        <path
          d="M1 1h8v5.5C9 9 7 10.5 5 11 3 10.5 1 9 1 6.5Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.4"
          strokeLinejoin="round"
        />
      </svg>
      {name}
    </Link>
  );
}
