export const connectOrderSocket = (
  paymentId: string,
  onStatusChange: (status: string) => void
) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL;
  const wsBase = baseUrl.replace(/^https/, "wss");

  const socketUrl = `${wsBase}/api/v1/seller/store/orders/${paymentId}/qr/callback`;

  const ws = new WebSocket(socketUrl);

  let timer: NodeJS.Timeout | null = null;

  ws.onopen = () => {
    timer = setTimeout(() => {
      ws.close();
      onStatusChange("timeout");
    }, 30_000);
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.status === "completed") {
        onStatusChange("completed");
        ws.close();
      } else if (data.status === "error") {
        onStatusChange("error");
        ws.close();
      } else if (data.status === "timeout") {
        onStatusChange("timeout");
        ws.close();
      }
    } catch (err) {
      {
      }
    }
  };

  ws.onerror = (err) => {
    console.warn("ws error", err);
  };

  ws.onclose = () => {
    if (timer) clearTimeout(timer);
  };

  const sendMsg = (msg: any) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  };

  return { ws, sendMsg };
};
