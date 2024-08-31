import React, { useCallback, useState } from "react";
import { useUserContext } from "../../contexts/UserContext";
import { useWebSocket } from "../../contexts/WebSocketContext";

const Files: React.FC = () => {
  const { user } = useUserContext();
  const socket = useWebSocket();

  const [files, setFiles] = useState<JSX.Element>(<></>);
  const updateFiles = useCallback(() => {
    if (socket === null) {
      return;
    }
    socket.emit("list", { token: user?.token }, (_: any) => {});
  }, [socket]);

  socket?.on("list", (response: any) => {
    let json = JSON.parse(response);
    let files = json["files"] == undefined ? [] : json["files"];
    let res = <></>;
    for (let i in files) {
      res = (
        <>
          {res}
          <div>
            <div className="grid grid-cols-4 justify-items-stretch text-center">
              <div>
                <p>{i}</p>
              </div>
              <div>
                <p>{files[i]["filename"]}</p>
              </div>
              <div>
                {files[i]["processed"] ? (
                  <button
                    type="button"
                    disabled
                    className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
                    onClick={() => {
                      updateFiles();
                    }}
                  >
                    {"Already Processed"}
                  </button>
                ) : (
                  <button
                    type="button"
                    className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
                    onClick={() => {
                      updateFiles();
                    }}
                  >
                    {"Process"}
                  </button>
                )}
                <p>{}</p>
              </div>
              <div>
                <p>
                  <button
                    type="button"
                    className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
                    onClick={() => {
                      updateFiles();
                    }}
                  >
                    {"Download"}
                  </button>
                </p>
              </div>
            </div>
          </div>
        </>
      );
    }
    setFiles(res);
  });

  return (
    <div className="grid grid-rows-2 ">
      <div className="flex w-screen items-center justify-center">
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
      <div className="w-screen">{files}</div>
    </div>
  );
};
export default Files;
