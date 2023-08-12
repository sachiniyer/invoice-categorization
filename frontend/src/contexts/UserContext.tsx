import React, { createContext, useContext, useState, ReactNode } from 'react';
import { User } from '../types/user';
import { register_user, login_user, update_password, delete_user } from '../api/user';

interface UserContextType {
    user: User | null;
    login: (userData: User) => boolean;
    register: (userData: User) => boolean;
    update: (password: string) => boolean;
    del: () => boolean;
    logout: () => boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);

    const login = (userData: User) => {
        try {
            if (userData !== null && userData.username !== '' && userData.password !== '' && process.env.REACT_APP_HAPI !== undefined) {
                login_user(userData.username, userData.password, process.env.REACT_APP_HAPI).then((response) => {
                    userData.token = response.jwt;
                    console.log(userData);
                    setUser(userData);
                    return true;
                });
            }
            else {
                throw new Error('Username and password are required');
            }
        }
        catch (e) {
            return false;
        }
        return false;
    };

    const register = (userData: User) => {
        try {
            if (userData !== null && userData.username !== '' && userData.password !== '' && process.env.REACT_APP_HAPI !== undefined) {
                register_user(userData.username, userData.password, process.env.REACT_APP_HAPI).then((response) => {
                    userData.token = response.jwt;
                    setUser(userData);
                    return true;
                })
            }
            else {
                throw new Error('Username and password are required');
            }
        }
        catch (e) {
            return false;
        }
        return false;
    };

    const update = (password: string) => {
        try {
            if (user !== null && user.token !== null && process.env.REACT_APP_HAPI !== undefined) {
                update_password(user.username, password, user.token, process.env.REACT_APP_HAPI).then((response) => {
                    let newUserData: User = {
                        username: user.username,
                        password: password,
                        token: response.jwt
                    };
                    setUser(newUserData);
                    return true;
                })
            }
            else {
                throw new Error('User is not logged in');
            }
        } catch (e) {
            return false;
        }
        return false;
    }

    const del = () => {
        try {
            if (user !== null && user.token !== null && process.env.REACT_APP_HAPI !== undefined) {
                delete_user(user.username, user.token, process.env.REACT_APP_HAPI).then((_) => {
                    setUser(null);
                    return true;
                })
            }
            else {
                throw new Error('User is not logged in');
            }
        } catch (e) {
            return false;
        }
        return false;
    }

    const logout = () => {
        setUser(null);
        return true;
    };

    return (
        <UserContext.Provider value={{ user, login, register, update, del, logout }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUserContext = (): UserContextType => {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUserContext must be used within a UserProvider');
    }
    return context;
};
