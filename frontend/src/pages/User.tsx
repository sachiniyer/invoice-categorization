import { useUserContext } from "../contexts/UserContext";
import LoginComponent from "../components/user/Login";
import ProfileComponent from "../components/user/Profile";

const User: React.FC = () => {
    const { user, loaded } = useUserContext();
    if (!loaded) {
        return (
            <div>
                <h1>Loading...</h1>
            </div>
        )
    }
    return (
        <div>
            {user === null || user.token === null ?
                <LoginComponent /> :
                <ProfileComponent />
            }
        </div>
    );
}

export default User;
