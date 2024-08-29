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
            <h1 className="text-center
                           text-7xl
                           text-blue-500
                           font-bold">
                LOGIN
            </h1>
            <div className="h-6"></div>
            <div className="flex
                            flex-col
                            justify-center
                            items-center
                            space-y-4">
                <div className="flex
                                flex-row
                                justify-center
                                items-center
                                space-x-4">
                    <input type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                </div>
                <button className="bg-blue-500
                                   hover:bg-blue-700
                                   text-white
                                   font-bold
                                   py-2
                                   px-4
                                   rounded"
                    onClick={handleLogin}>
                    Login
                </button>
                <button className="bg-blue-500
                                   hover:bg-blue-700
                                   text-white
                                   font-bold
                                   py-2
                                   px-4
                                   rounded"
                    onClick={handleRegister}>
                    Register
                </button>
            </div>
        </div>
    );
};

export default LoginComponent;
