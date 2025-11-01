export const useOrderWebSocket = (paymentId: string) => {
  const socketUrl = `wss://dev-back.cheap-bob.store/api/v1/orders/${paymentId}/qr/callback`;

  const ws = new WebSocket(socketUrl);

  ws.onopen = () => {
    console.log("connected!");
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    console.log("message received", data);
  };

  ws.onerror = (err) => {
    console.error("ws error", err);
  };

  ws.onclose = () => {
    console.log("ws is closed");
  };

  const sendMsg = (msg: any) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  };

  return { ws, sendMsg };
};
