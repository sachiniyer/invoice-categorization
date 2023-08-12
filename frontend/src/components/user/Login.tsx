import React, { useState } from 'react';
import { useUserContext } from '../../contexts/UserContext';
import { User } from '../../types/user';

const LoginComponent: React.FC = () => {
    const { login } = useUserContext();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = () => {
        const userData: User = {
            username: username,
            password: password,
            token: null
        };
        if (login(userData)) {
            window.location.href = '/';
        }
        else {
            alert('Login Failed');
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
        </div>
    );
};

export default LoginComponent;
