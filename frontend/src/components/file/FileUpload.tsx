import React, { useCallback, useState } from "react";
import { useWebSocket } from "../../contexts/WebSocketContext";
import { useUserContext } from "../../contexts/UserContext";

const FileUpload: React.FC = () => {
  const { user } = useUserContext();
  const socket = useWebSocket();

  const CHUNK_SIZE = 1024 * 256 * 1;

  const randomString = useCallback((length: number) => {
    const characters =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let result = "";
    for (let i = 0; i < length; i++) {
      result += characters.charAt(
        Math.floor(Math.random() * characters.length)
      );
    }
    return result;
  }, []);

  const uploadFile = useCallback(
    async (file: File) => {
      if (socket === null) {
        return;
      }

      const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
      let currentChunk = 0;

      const fileid = randomString(10);

      const reader = new FileReader();

      reader.onload = (e) => {
        if (socket === null) {
          return;
        }

        const fileData = e.target?.result as ArrayBuffer;

        if (fileData) {
          const base64String = btoa(
            new Uint8Array(fileData).reduce(
              (data, byte) => data + String.fromCharCode(byte),
              ""
            )
          );
          const payload = {
            filename: file.name,
            token: user?.token,
            fileid: fileid,
            chunk_number: currentChunk,
            total_chunks: totalChunks,
            chunk: base64String,
          };

          socket.emit("upload", payload);

          currentChunk++;

          if (currentChunk <= totalChunks) {
            setTimeout(() => {
              loadNextChunk();
            }, 100);
          } else {
            console.log("File upload complete");
          }
        }
      };

      const loadNextChunk = () => {
        const start = currentChunk * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const blob = file.slice(start, end);
        reader.readAsArrayBuffer(blob);
      };

      loadNextChunk();
    },
    [socket, CHUNK_SIZE, user?.token, randomString]
  );

  const handleFiles = useCallback(
    (files: FileList) => {
      if (process.env.REACT_APP_DISABLE?.toLowerCase() === "true") {
        alert("File upload is disabled for demo, run it locally");
        return;
      }

      console.log("Dropped files:", files);
      if (socket == null) {
        return;
      }
      Array.from(files).forEach((file) => {
        uploadFile(file);
      });
    },
    [socket, uploadFile]
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
