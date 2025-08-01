import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import {BrowserRouter, Routes,Route} from "react-router"
import MainWrapper from './layouts/MainWrapper';

import Index from "./views/base/Index"
import Register from './views/auth/Register';
import Login from './views/auth/Login';
import Logout from './views/auth/Logout';
import ForgotPassword from './views/auth/ForgotPassword';
import CreateNewPassword from './views/auth/CreateNewPassword';
import CourseDetail from './views/base/CourseDetail';
import apiInstance from './utils/axios';
import CartId from './views/plugin/CartId';
import { CartContext, ProfileContext } from './views/plugin/Context';
import Cart from './views/base/Cart';
import Checkout from './views/base/Checkout';
import Success from './views/base/Success';
import Search from './views/base/Search';
import StudentChangePassword from './views/student/ChangePassword';
import StudentDashboard from './views/student/Dashboard';
import StudentCourses from './views/student/Courses';
import StudentCourseDetail from './views/student/CourseDetail';
import StudentWishlist from './views/student/Wishlist';
import StudentProfile from './views/student/Profile';
import useAxios from './utils/useAxios';
import UserData from './views/plugin/UserData';
import Dashoard from "./views/instructor/Dashboard";
import Courses from "./views/instructor/Courses"
import Review from './views/instructor/Review';
import Students from './views/instructor/Students';
import Earning from './views/instructor/Earning';
function App() {

 const [cartCount, setCartCount] = useState(0);
 const [profile,setProfile] = useState([]);

 const fetchCartCount = () => {
  apiInstance.get(`course/cart-list/${CartId()}`)
    .then((res) => {
      setCartCount(res.data?.length);
    })
    .catch(() => {
      setCartCount(0); // fallback
    });
};
const fetchProfile = () => {
  useAxios.get(`user/profile/${UserData()?.user_id}/`)
  .then((res)=>{
    setProfile(res.data);
  });
};

useEffect(() => {
  fetchCartCount();
  fetchProfile();
}, []);

  return (
    <CartContext.Provider value={[cartCount,setCartCount]}>
      <ProfileContext.Provider value={[profile,setProfile]}>
      <BrowserRouter>
        <MainWrapper>
          <Routes>
            <Route path='/register/' element={<Register/>} />
            <Route path='/login/' element={<Login/>} />
            <Route path='/logout/' element={<Logout/>} />
            <Route path='/forgot-password/' element={<ForgotPassword/>} />
            <Route path='/create-new-password/' element={<CreateNewPassword/>} />
           



            <Route path="/" element={<Index/>} />
            <Route path="/course-detail/:slug/" element={<CourseDetail />} />
            <Route path='/cart/' element={<Cart/>} />
            <Route path="/checkout/:order_oid/" element={<Checkout />} />
            <Route path='payment-success/:order_oid/' element={<Success/>} />
            <Route path='search/' element={<Search/>} />


            {/* students routes */}
            <Route path="/student/dashboard/" element={ <StudentDashboard/> } />
            <Route path='/student/change-password/' element={ <StudentChangePassword/> }  />
            <Route path='/student/courses/' element={ < StudentCourses/>} />
            <Route path='/student/courses/:enrollment_id/' element={< StudentCourseDetail />} />
            <Route path='/student/wishlist/' element={< StudentWishlist />} />
            <Route path='/student/profile' element={<StudentProfile/>} />

            {/* teacher routes */}

            <Route path='/instructor/dashboard/' element={<Dashoard/>} />
            <Route path='/instructor/courses/' element={<Courses/>} />
            <Route path='/instructor/reviews/' element={<Review/>} />
            <Route path='instructor/students/' element={<Students/>} />
            <Route path='instructor/earning/' element={<Earning/>} />



          </Routes>
        </MainWrapper>
      
      </BrowserRouter>
      </ProfileContext.Provider>
    </CartContext.Provider>
      
  )
}

export default App
