import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';

function UserData() {
    let access_token = Cookies.get("access_token");
    let refresh_token = Cookies.get("refresh_token");

    if (access_token && refresh_token) {
        const token = refresh_token;
        const decoded = jwtDecode(token);

        return decoded;
    }
}

export default UserData;
