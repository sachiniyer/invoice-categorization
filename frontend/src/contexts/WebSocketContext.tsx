import React, { createContext, useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";

const WebSocketContext = createContext<Socket | null>(null);
export const useWebSocket = () => React.useContext(WebSocketContext);

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  useEffect(() => {
    if (!process.env.REACT_APP_WAPI) {
      throw new Error("REACT_APP_WAPI is not defined");
    }
    const newSocket = io(process.env.REACT_APP_WAPI, {
      forceNew: true,
    });
    setSocket(newSocket);
    return () => {
      newSocket.disconnect();
    };
  }, []);

  return (
    <WebSocketContext.Provider value={socket}>
      {children}
    </WebSocketContext.Provider>
  );
};
