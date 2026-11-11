import { Link } from "react-router";

import type { Product } from "../lib/types";
import { Field } from "./ui";

interface ProductSelectProps {
  id: string;
  products: Product[];
  value: string;
  onChange: (code: string) => void;
  label?: string;
}

export function ProductSelect({
  id,
  products,
  value,
  onChange,
  label = "Producto",
}: ProductSelectProps) {
  if (products.length === 0) {
    return (
      <Field label={label} htmlFor={id}>
        <select id={id} className="control" disabled>
          <option>Aún no hay productos</option>
        </select>
        <p className="mt-1 text-[0.82rem] text-ink-soft">
          <Link to="/productos" className="font-semibold text-info">
            Crea el primero en Productos
          </Link>{" "}
          para poder usar esta pantalla.
        </p>
      </Field>
    );
  }
  return (
    <Field label={label} htmlFor={id}>
      <select
        id={id}
        className="control"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {products.map((product) => (
          <option key={product.code} value={product.code}>
            {product.code}: {product.name}
          </option>
        ))}
      </select>
    </Field>
  );
}
