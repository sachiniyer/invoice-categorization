import React, { useCallback, useState, useEffect } from "react";
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
  }, [socket, user?.token]);

  const processFile = useCallback(
    (fileid: string) => {
      if (socket === null) {
        return;
      }
      socket.emit(
        "process",
        { token: user?.token, fileid: fileid },
        (_: any) => {}
      );
    },
    [socket, user?.token]
  );

  const downloadFile = useCallback(
    (fileid: string) => {
      if (socket === null) {
        return;
      }
      socket.emit(
        "get",
        { token: user?.token, fileid: fileid },
        (_: any) => {}
      );
    },
    [socket, user?.token]
  );

  const deleteFile = useCallback(
    (fileid: string) => {
      if (socket === null) {
        return;
      }
      socket.emit(
        "delete",
        { token: user?.token, fileid: fileid },
        (_: any) => {}
      );
    },
    [socket, user?.token]
  );

  useEffect(() => {
    const processButton = (status: string, fileid: string) => {
      if (status === "not processed") {
        return (
          <button
            type="button"
            className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
            onClick={() => {
              processFile(fileid);
              setTimeout(() => {
                updateFiles();
              }, 1000);
            }}
          >
            {"Process"}
          </button>
        );
      }
      if (status === "processing") {
        return (
          <p>
            <button
              type="button"
              disabled
              className="text-white bg-gray-500 hover:bg-gray-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
            >
              {"Processing"}
            </button>
          </p>
        );
      }
      if (status === "processed") {
        return (
          <p>
            <button
              type="button"
              disabled
              className="text-white bg-gray-500 hover:bg-gray-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
            >
              {"Already Processed"}
            </button>
          </p>
        );
      }
    };

    const downloadButton = (status: string, fileid: string) => {
      if (status === "processed") {
        return (
          <button
            type="button"
            className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
            onClick={() => downloadFile(fileid)}
          >
            {"Download"}
          </button>
        );
      }
      return (
        <button
          type="button"
          disabled
          className="text-white bg-gray-500 hover:bg-gray-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
        >
          {"Download"}
        </button>
      );
    };

    socket?.on("list", (response: any) => {
      let json = JSON.parse(response);
      let files = json["files"] === undefined ? [] : json["files"];
      let res = <></>;
      for (let i in files) {
        res = (
          <>
            {res}
            <div>
              <div className="grid grid-cols-5 justify-items-stretch text-center">
                <div>
                  <p>{i}</p>
                </div>
                <div>
                  <p>{files[i]["filename"]}</p>
                </div>
                <div>
                  {processButton(files[i]["processed"], i)}
                  <p>{}</p>
                </div>
                <div>
                  <p>{downloadButton(files[i]["processed"], i)}</p>
                </div>
                <div>
                  <p>
                    <button
                      type="button"
                      className="text-white bg-blue-500 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2"
                      onClick={() => {
                        deleteFile(i);
                        setTimeout(() => {
                          updateFiles();
                        }, 1000);
                      }}
                    >
                      {"Delete"}
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
  }, [socket, updateFiles, processFile, deleteFile, downloadFile]);

  useEffect(() => {
    socket?.on("download", (response: any) => {
      let data = response.data.join("\n");
      let blob = new Blob([data], { type: "text/plain" });
      let url = window.URL.createObjectURL(blob);
      let a = document.createElement("a");
      a.href = url;
      a.download = "download";
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }, [socket]);

  return (
    <div>
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
