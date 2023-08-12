import { useUserContext } from "../contexts/UserContext";
import LoginComponent from "../components/user/Login";

const User: React.FC = () => {
    const { user } = useUserContext();
    if (user) {
        return (
            <div>
                <h1>Welcome {user.username}</h1>
            </div>
        );
    }
    return (
        <div>
            <LoginComponent />
        </div>
    )
}

export default User;
