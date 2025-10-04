import type { Offset } from "@interface";

export const toMinutes = (t?: string): number | null => {
  if (!t) return null;
  const [hh = "", mm = ""] = t.split(":");
  const h = Number(hh);
  const m = Number(mm);
  if (Number.isNaN(h) || Number.isNaN(m)) return null;
  return (((h * 60 + m) % 1440) + 1440) % 1440;
};

export const fromMinutes = (mins: number): string => {
  const m = ((mins % 1440) + 1440) % 1440;
  const hh = String(Math.floor(m / 60)).padStart(2, "0");
  const mm = String(m % 60).padStart(2, "0");
  return `${hh}:${mm}:00`;
};

export const diffFromClose = (
  close?: string,
  pickup?: string
): number | null => {
  const c = toMinutes(close);
  const p = toMinutes(pickup);
  if (c == null || p == null) return null;
  return (c - p + 1440) % 1440;
};

export const minutesToOffset = (mins: number | null): Offset => {
  if (mins == null) return { hour: 0, min: 0 };
  const m = ((mins % 1440) + 1440) % 1440;
  return { hour: Math.floor(m / 60), min: m % 60 };
};
