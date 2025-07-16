//utils/axios.js


import axios from "axios"
import Cookie from "js-cookie";
import { getRefreshToken, isAccessTokenExpired, setAuthUser } from "./auth";


const apiInstance = axios.create({
    baseURL: "http://127.0.0.1:8000/api/v1/",
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    }
});

apiInstance.interceptors.request.use(
   async (config) => {
        const accessToken = Cookie.get("access_token");

        if(accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        //if access token is expired , attempt to refresh it
        if(isAccessTokenExpired(accessToken)) {
            const refreshToken = Cookie.get("refresh_token"); // update for consistency

            if(refreshToken){
                try {
                    const response = await getRefreshToken(refreshToken);
                    setAuthUser(response.data.access, response.data.refresh);
                    config.headers.Authorization = `Bearer ${response.data.access}`;
                } catch (error) {
                    console.error("Token refresh failed",error);
                }

            }
        }

        return config;

    },
    (error) => Promise.reject(error)
);


// response interceptor for handling error

apiInstance.interceptors.response.use(
    (response) => response,
    (error) => {
        if(error.response && error.response.status === 401){
            console.error("Unauthorized access - you may nedd to log,in",error);
        }
        return Promise.reject(error);
    }
)

export default apiInstance;