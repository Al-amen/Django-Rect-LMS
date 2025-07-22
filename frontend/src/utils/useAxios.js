import axios from "axios"
import Cookie from "js-cookie";
import { getRefreshToken, isAccessTokenExpired, setAuthUser } from "./auth";



// Create an Axios instance with default settings
const useAxios = axios.create({
    baseURL: "http://127.0.0.1:8000/api/v1/",
    timeout: 10000000,
    headers: {
        "Content-Type": "application/json",
    },
});

// Request interceptor for adding authentication token if available
useAxios.interceptors.request.use(
    async (config) => {
        const accessToken = Cookie.get("access_token"); // Updated cookie names for consistency with your app

        // If the access token exists, add it to the Authorization header
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }

        // If the access token is expired, attempt to refresh it
        if (isAccessTokenExpired(accessToken)) {
            const refreshToken = Cookie.get("refresh_token"); // Updated for consistency
            if (refreshToken) {
                try {
                    const response = await getRefreshToken(refreshToken);

                    // Update the token cookies and headers
                    setAuthUser(response.data.access, response.data.refresh);
                    config.headers.Authorization = `Bearer ${response.data.access}`;
                } catch (error) {
                    // Handle refresh token failure (e.g., log out user or show an error message)
                    console.error("Token refresh failed:", error);
                }
            }
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for handling errors
useAxios.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle specific error cases if needed
        if (error.response && error.response.status === 401) {
            // Handle unauthorized errors (e.g., redirect to login)
            console.error("Unauthorized access - you may need to log in:", error);
        }

        return Promise.reject(error);
    }
);

export default useAxios;
