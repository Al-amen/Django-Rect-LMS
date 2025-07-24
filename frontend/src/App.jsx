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
import { CartContext } from './views/plugin/Context';
import Cart from './views/base/Cart';
import Checkout from './views/base/Checkout';
import Success from './views/base/Success';
import Search from './views/base/Search';
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
useEffect(() => {
  fetchCartCount();
}, []);

  return (
    <CartContext.Provider value={[cartCount,setCartCount]}>
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



          </Routes>
        </MainWrapper>
      
      </BrowserRouter>
    </CartContext.Provider>
      
  )
}

export default App
