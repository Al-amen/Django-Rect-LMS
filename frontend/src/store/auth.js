
// import {create} from "zustand";
// import {mountStoreDevtool} from "simple-zustand-devtools";


// const useAuthStore = create((set,get)=>({
//     allUserData:null,
//     loading:false,

//     user: () => ({
//         user_id:get().allUserData?.user_id || null,
//         username:get().allUserData?.username || null,

//     }),

//     setUser:(user) => set({
//         allUserData:user
//     }),
//     setLoading: (loading) => set({loading}),
//     isLoggedIn: () => get().allUserData !== null,


// }));

// if(import.meta.env.DEV) {
//     mountStoreDevtool("Store",useAuthStore);
// }

// export {useAuthStore};


//store/auth.js

import { create } from "zustand";
import { mountStoreDevtool } from "simple-zustand-devtools";

const useAuthStore = create((set, get) => ({
  allUserData: null,
  loading: false,

  setUser: (user) => set({ allUserData: user }),
  setLoading: (loading) => set({ loading }),
}));

if (import.meta.env.DEV) {
  mountStoreDevtool("Store", useAuthStore);
}

export { useAuthStore };

// Utility helpers
export const isLoggedIn = () => useAuthStore.getState().allUserData !== null;

export const getUser = () => {
  const user = useAuthStore.getState().allUserData;
  return {
    user_id: user?.user_id || null,
    username: user?.username || null,
  };
};
