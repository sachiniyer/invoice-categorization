import React, { useCallback, useState } from "react";
import { useWebSocket } from "../../contexts/WebSocketContext";
import { useUserContext } from "../../contexts/UserContext";

const FileUpload: React.FC = () => {
  const { user } = useUserContext();
  const socket = useWebSocket();

  const uploadFile = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (socket === null) {
        return;
      }

      const data = e.target?.result;
      if (data instanceof ArrayBuffer) {
        const buffer = new Uint8Array(data);
        socket.emit("upload", {
          filename: file.name,
          token: user?.token,
          chunk: buffer,
        });
      }
    };
    reader.readAsArrayBuffer(file);
  }, []);

  const handleFiles = useCallback(
    (files: FileList) => {
      console.log("Dropped files:", files);
      if (socket == null) {
        return;
      }
      for (let f in files) {
        uploadFile(files[f]);
      }
    },
    [socket]
  );

  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);

      const files = e.dataTransfer.files;
      handleFiles(files);
    },
    [handleFiles]
  );

  const fileInputRef = React.createRef<HTMLInputElement>();

  const handleFileClick = useCallback(() => {
    fileInputRef.current?.click();
  }, [fileInputRef]);

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files) {
        handleFiles(files);
      }
    },
    [handleFiles]
  );

  return (
    <div
      className={`border-4 border-dashed p-8 m-4 ${
        isDragOver ? "border-blue-500" : "border-gray-400"
      }`}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleFileClick}
    >
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        onChange={handleFileInputChange}
      />
      {isDragOver ? (
        <p>Drop the files here</p>
      ) : (
        <p>Drag and drop files here or click to choose</p>
      )}
    </div>
  );
};

export default FileUpload;
