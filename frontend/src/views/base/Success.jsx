import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import BaseHeader from '../partials/BaseHeader'
import BaseFooter from '../partials/BaseFooter'
import apiInstance from '../../utils/axios';

function Success() {
    const [order,setOrder] = useState([]);
    const [orderMessage,setOrderMessage] = useState("");

    const param = useParams();
    const urlParm = new URLSearchParams(window.location.search);
    const  sessionId = urlParm.get("session_id");
    const paypalOrderId = urlParm.get("paypal_order_id");
    console.log(sessionId);
    console.log(paypalOrderId);
    console.log(param);

    useEffect(()=>{
        const formdata = new FormData();
        formdata.append("order_oid",param.order_oid);
        formdata.append("session_id",sessionId);
        formdata.append("paypal_order_id",paypalOrderId);

        setOrderMessage("Processing Payment");

        try {
            apiInstance.post(`payment/payment-sucess/`,formdata).then((res)=>{
                console.log(res.data);
                setOrderMessage(res.data.message);
            })
        } catch (error) {
            console.log(error);
        }
    },[]);

  //  console.log(orderMessage);

    return (
        <>
            <BaseHeader />

            <section className="pt-0  position-relative overflow-hidden my-auto">
                <div className="container position-relative">
                    <div className="row g-5 align-items-center justify-content-center">
                        {/* Payment Successfull */}
                        {orderMessage === "Payment Successfull" && (
                            <>
                                <div className="col-lg-5">
                                    <h1 className="text-success">Enrollment Successful!</h1>
                                    <p>Your enrollment was successfull, please visit your dashboard to start course now.</p>
                                </div>
                                <div className="col-lg-7 text-center">
                                    <img src="https://i.pinimg.com/originals/0d/e4/1a/0de41a3c5953fba1755ebd416ec109dd.gif" className="h-300px h-sm-400px h-md-500px h-xl-700px" alt="" />
                                </div>
                            </>
                        )}

                        {/* Already Paid */}
                        {orderMessage === "Already Paid" && (
                            <>
                                <div className="col-lg-5">
                                    <h1 className="text-success">Enrollment Successful!</h1>
                                    <p>Your enrollment was successfull, please visit your dashboard to start course now.</p>
                                </div>
                                <div className="col-lg-7 text-center">
                                    <img src="https://i.pinimg.com/originals/0d/e4/1a/0de41a3c5953fba1755ebd416ec109dd.gif" className="h-300px h-sm-400px h-md-500px h-xl-700px" alt="" />
                                </div>
                            </>
                        )}

                        {/* Processing */}
                        {orderMessage === "Processing Payment" && (
                            <>
                                <div className="col-lg-5">
                                    <h1 className="text-warning">
                                        Processing Payment <i className="fas fa-spinner fa-spin"></i>
                                    </h1>
                                    <p> Hey there, hold on while we process your payment, please do not leave the page.</p>
                                </div>
                                <div className="col-lg-7 text-center">
                                    <img sty src="https://www.icegif.com/wp-content/uploads/2023/07/icegif-1259.gif" className="h-300px h-sm-400px h-md-500px h-xl-700px" alt="" />
                                </div>
                            </>
                        )}

                        {/* Failed */}
                        {orderMessage === "Payment Failed" && (
                            <>
                                <div className="col-lg-5">
                                    <h1 className="text-danger">Payment Failed 😔</h1>
                                    <p>
                                        Unfortunately, phew! Your payment did not go through. <br /> Please try again.
                                    </p>
                                    <button type="button" className="btn btn-danger mb-0 rounded-2">
                                        Try again <i className="fas fa-repeat"></i>
                                    </button>
                                </div>
                                <div className="col-lg-7 text-center">
                                    <img sty src="https://media3.giphy.com/media/h4OGa0npayrJX2NRPT/giphy.gif?cid=790b76117pc6298jypyph0liy6xlp3lzb7b2y405ixesujeu&ep=v1_stickers_search&rid=giphy.gif&ct=e" className="h-300px h-sm-400px h-md-500px h-xl-700px" alt="" />
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </section>



            <BaseFooter />
        </>
    )
}

export default Success