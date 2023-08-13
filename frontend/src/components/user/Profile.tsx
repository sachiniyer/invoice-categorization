import React, { useState } from "react";
import { useUserContext } from "../../contexts/UserContext";


const ProfileComponent: React.FC = () => {
    const { user, logout, del, update } = useUserContext();
    const [password, setPassword] = useState('');

    const update_password = () => {
        if (password !== '') {
            update(password);
        }
    }

    let res = "Not Logged In";
    if (user !== null && user.username !== null) {
        res = user.username;
    }

    return (
        <div>
            <h1>Profile</h1>
            <h2>{res}</h2>
            <button onClick={() => logout()}>Logout</button>
            <button onClick={() => del()}>Delete Account</button>
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={() => update_password()}>Update Password</button>

        </div>
    );
}

export default ProfileComponent;
