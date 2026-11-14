import { useEffect, useState } from "react";

import { api } from "./api";
import type { Product } from "./types";
import { useQuery } from "./useQuery";
import type { QueryState } from "./useQuery";

interface ProductSelection {
  products: QueryState<Product[]>;
  selected: string;
  select: (code: string) => void;
}

/** Catálogo de productos y el que está elegido en la pantalla. */
export function useProducts(): ProductSelection {
  const products = useQuery(() => api<Product[]>("/products"), []);
  const [selected, setSelected] = useState("");

  // Mientras no haya elección, toma el primero del catálogo. No corrige
  // una elección existente: el producto recién creado aún no figura en
  // la lista que se está recargando, y los productos no se eliminan.
  useEffect(() => {
    const first = products.data?.[0];
    if (selected === "" && first) setSelected(first.code);
  }, [products.data, selected]);

  return { products, selected, select: setSelected };
}
