import React, { useCallback, useState } from 'react';
import { useWebSocket } from '../../contexts/WebSocketContext';

const FileUpload: React.FC = () => {
    const socket = useWebSocket();
    const handleFiles = useCallback((files: FileList) => {
        if (socket) {
            socket.emit('message', files);
        }
        console.log('Dropped files:', files);
    }, [socket]);


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
        e.dataTransfer.dropEffect = 'copy';
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
            className={`border-4 border-dashed p-8 m-4 ${isDragOver ? 'border-blue-500' : 'border-gray-400'
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
            {isDragOver ? <p>Drop the files here</p> : <p>Drag and drop files here or click to choose</p>}
        </div>
    );
};

export default FileUpload;
