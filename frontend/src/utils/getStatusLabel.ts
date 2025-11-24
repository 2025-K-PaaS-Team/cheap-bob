const STATUS_LABELS: Record<string, string> = {
  reservation: "주문이 들어갔어요!",
  accept: "픽업이 확정됐어요!",
  cancel: "주문이 취소됐어요.",
};

export const getStatusLabel = (status: string) => STATUS_LABELS[status] || "-";
