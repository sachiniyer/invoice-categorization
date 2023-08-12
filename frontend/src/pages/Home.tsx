import FileUpload from '../components/file/FileUpload';
import { useUserContext } from "../contexts/UserContext";

const Home: React.FC = () => {
    const { user } = useUserContext();
    if (user === null || user.token === null) {
        window.location.href = '/user';
    }

    return (
        <div>
            <FileUpload />
        </div>
    );
}

export default Home;
