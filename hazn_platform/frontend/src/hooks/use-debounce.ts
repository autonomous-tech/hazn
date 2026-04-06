"use client";

/**
 * Debounce hook for search inputs.
 *
 * Returns a debounced version of the input value that only
 * updates after the specified delay (default 300ms). Useful
 * for avoiding excessive API calls during typing.
 */

import { useEffect, useState } from "react";

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}
