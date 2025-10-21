import type { TimeStamp } from "@interface/common/types";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

const normalizeToIsoUtc = (raw: TimeStamp): string => {
  let s = String(raw).trim();

  s = s.replace(" ", "T");
  s = s.replace(/(\.\d{3})\d+/, "$1");

  const hasOffset = /[zZ]$|[+\-]\d{2}:?\d{2}$/.test(s);
  if (!hasOffset) s += "Z";

  return s;
};

export const formatDate = (date: TimeStamp) => {
  if (!date) return;

  const formattingString = "YYYY-MM-DD HH:mm:ss";

  const isoUtc = normalizeToIsoUtc(date);
  return dayjs.utc(isoUtc).tz("Asia/Seoul").format(formattingString);
};
