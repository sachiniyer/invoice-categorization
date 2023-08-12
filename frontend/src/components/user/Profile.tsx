import React, { useState } from 'react';
import { useUserContext } from "../../contexts/UserContext";


const ProfileComponent: React.FC = () => {
    const { user } = useUserContext();

    if (user === null || user.token === null) {
        window.location.href = '/user';
    }

    let res = "Not Logged In";
    if (user !== null && user.username !== null) {
        res = user.username;
    }
    return (
        <div>
            <h1>Profile</h1>
            <h2>{res}</h2>
        </div>
    );
}
