import FileUpload from '../components/file/FileUpload';
import Files from '../components/file/Files'
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
                <h1 className="text-center
                               text-4xl">
                    {"Please "}
                    <a href="/user" className="text-blue-500">
                        {"login"}
                    </a>
                    {" to continue"}
                </h1>
            </div>
        )
    }

    return (
        <div>
            <FileUpload />
            <Files />
        </div>
    );
}

export default Home;
