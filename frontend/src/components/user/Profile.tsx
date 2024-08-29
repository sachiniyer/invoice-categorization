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
            <h1 className="text-center
                           text-7xl
                           text-blue-500
                           font-bold">
                PROFILE
            </h1>
            <div className="h-6"></div>
            <h2 className="text-center
                           text-3xl
                           font-bold">
                {res}
            </h2>
            <div className="h-10"></div>
            <div className="flex
                            flex-col
                            justify-center
                            items-center
                            space-y-4">
                <button className="bg-blue-500
                                   hover:bg-blue-700
                                   text-white
                                   font-bold
                                   py-2
                                   px-4
                                   rounded"
                    onClick={() => logout()}>
                    Logout
                </button>
                <div className="flex
                                flex-row
                                justify-center
                                items-center
                                space-x-4">
                    <input type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <button className="bg-blue-500
                                       hover:bg-blue-700
                                       text-white
                                       font-bold
                                       py-2
                                       px-4
                                       rounded"
                        onClick={() => update_password()}>
                        Update Password
                    </button>

                </div>
                <button className="bg-blue-500
                                   hover:bg-blue-700
                                   text-white
                                   font-bold
                                   py-2
                                   px-4
                                   rounded"
                    onClick={() => del()}>
                    Delete Account
                </button>
            </div>
        </div>
    );
}

export default ProfileComponent;
