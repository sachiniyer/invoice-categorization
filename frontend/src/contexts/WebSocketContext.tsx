import React, { createContext, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import env from "react-dotenv";

const WebSocketContext = createContext<Socket | null>(null);
export const useWebSocket = () => React.useContext(WebSocketContext);

interface WebSocketProviderProps {
    children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
    const [socket, setSocket] = useState<Socket | null>(null);
    useEffect(() => {
        const newSocket = io(env.API);
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
