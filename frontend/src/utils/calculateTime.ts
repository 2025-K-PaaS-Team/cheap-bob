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

export const pad2 = (n: number) => String(n).padStart(2, "0");

export const toHM = (t?: string) => {
  const [h = "0", m = "0"] = (t || "").split(":");
  return { h: Number(h) || 0, m: Number(m) || 0 };
};

export const minusOffset = (h: number, m: number, oh: number, om: number) => {
  const base = h * 60 + m;
  const off = (oh * 60 + om) % 1440;
  const x = (((base - off) % 1440) + 1440) % 1440;
  return { h: Math.floor(x / 60), m: x % 60 };
};

export const clampNum = (raw: string, max: number) => {
  const v = raw.replace(/\D/g, "");
  if (!v) return 0;
  const n = Math.min(max, Math.max(0, parseInt(v.slice(-2), 10) || 0));
  return n;
};
