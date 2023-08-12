import React from 'react';
import Header from './components/Header';
import Home from './pages/Home';
import User from './pages/User';
import { UserProvider } from './contexts/UserContext'
import { WebSocketProvider } from './contexts/WebSocketContext';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'

const App: React.FC = () => {
    return (
        <div>
            <Header />
            <main>
                <UserProvider>
                    <WebSocketProvider>
                        <Router>
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/user" element={<User />} />
                            </Routes>
                        </Router>
                    </WebSocketProvider>
                </UserProvider>
            </main>
        </div>
    );
};

export default App;
