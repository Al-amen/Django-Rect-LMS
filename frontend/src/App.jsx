import { useState } from 'react'
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

function App() {


  return (
    <BrowserRouter>
      <MainWrapper>
        <Routes>
          <Route path='/register/' element={<Register/>} />
          <Route path='/login/' element={<Login/>} />
          <Route path='/logout/' element={<Logout/>} />
          <Route path='/forgot-password/' element={<ForgotPassword/>} />
          <Route path='/create-new-password/' element={<CreateNewPassword/>} />



          <Route path="/" element={<Index/>} />

        </Routes>
      </MainWrapper>
    
    </BrowserRouter>
      
  )
}

export default App
