import React from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';

const App: React.FC = () => {
    return (
        <div>
            <Header />
            <main>
                <FileUpload />
            </main>
        </div>
    );
};

export default App;
