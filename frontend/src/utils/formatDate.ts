import type { TimeStamp } from "@interface/common/types";
import dayjs from "dayjs";

export const formatDate = (date: TimeStamp) => {
  if (!date) return;

  const formattingString = "YYYY-MM-DD HH:mm:ss";

  return dayjs(date).format(formattingString);
};
