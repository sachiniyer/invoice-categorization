import React, { useCallback, useState } from "react";
import { useUserContext } from "../../contexts/UserContext";
import { useWebSocket } from "../../contexts/WebSocketContext";

const Files: React.FC = () => {
  const { user } = useUserContext();
  const socket = useWebSocket();

  const [files, setFiles] = useState<string[]>([]);
  const updateFiles = useCallback(() => {
    if (socket === null) {
      return;
    }
    socket.emit("list", { token: user?.token }, (_: any) => {});
  }, [socket]);

  socket?.on("list", (response: any) => {
    setFiles(response["files"] == undefined ? [] : response["files"]);
  });

  return (
    <div className="flex items-center justify-center">
      <div>
        <button
          type="button"
          className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
          onClick={() => {
            updateFiles();
          }}
        >
          {"Refresh File List"}
        </button>
      </div>
      <p>{files}</p>
    </div>
  );
};
export default Files;
