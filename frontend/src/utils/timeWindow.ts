import dayjs, { Dayjs } from "dayjs";

export const parseToday = (now: dayjs.Dayjs, hhmmss?: string | null) => {
  if (!hhmmss) return null;
  const [hh, mm, ss] = [
    Number(hhmmss.slice(0, 2)),
    Number(hhmmss.slice(3, 5)),
    Number(hhmmss.slice(6, 8)),
  ];
  return now.set("hour", hh).set("minute", mm).set("second", ss);
};

export const buildWindow = (
  start?: string,
  end?: string
): { start: Dayjs | null; end: Dayjs | null } => {
  const now = dayjs();
  return {
    start: parseToday(now, start),
    end: parseToday(now, end),
  };
};

export const inWindow = (
  now: dayjs.Dayjs,
  start: dayjs.Dayjs | null,
  end: dayjs.Dayjs | null
) => {
  if (!start || !end) return false;
  const t = now.valueOf();
  return t >= start.valueOf() && t <= end.valueOf();
};
