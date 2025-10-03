import axios, { AxiosError } from "axios";

export const formatErrMsg = (e: unknown): string => {
  if (axios.isAxiosError(e)) {
    const data = (e as AxiosError<any>).response?.data;

    if (Array.isArray(data?.detail)) {
      const firstErr = data.detail[0];
      return firstErr?.msg ?? "오류가 발생했습니다.";
    }

    if (typeof data.detail === "string") return data.detail;

    return (
      data?.error?.message ??
      data?.message ??
      e.message ??
      "오류가 발생했습니다."
    );
  }

  return e instanceof Error ? e.message : String(e);
};
