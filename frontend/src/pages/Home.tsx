import FileUpload from '../components/file/FileUpload';
import { useUserContext } from "../contexts/UserContext";

const Home: React.FC = () => {
    const { user, loaded } = useUserContext();
    if (!loaded) {
        return (
            <div>
                <h1>Loading...</h1>
            </div>
        )
    }

    if (user === null || user.token === null) {
        return (
            <div>
                <h1>{"Please login to continue"}</h1>
            </div>
        )
    }

    return (
        <div>
            <FileUpload />
        </div>
    );
}

export default Home;
