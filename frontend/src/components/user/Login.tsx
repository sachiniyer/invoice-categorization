import React, { useState } from 'react';
import { useUserContext } from '../../contexts/UserContext';
import { User } from '../../types/user';

const LoginComponent: React.FC = () => {
    const { login, register } = useUserContext();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = () => {
        const userData: User = {
            username: username,
            password: password,
            token: null
        };
        if (!login(userData)) {
            alert('Login Failed');
        }
    };

    const handleRegister = () => {
        const userData: User = {
            username: username,
            password: password,
            token: null
        };
        if (!register(userData)) {
            alert('Register Failed');
        }
    };

    return (
        <div>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>Login</button>
            <button onClick={handleRegister}>Register</button>
        </div>
    );
};

export default LoginComponent;
