import React, { useContext, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";
import apiInstance from "../../utils/axios";
import CartId from "../plugin/CartId";
import { CartContext } from "../plugin/Context";
import Toast from "../plugin/Toast";
import { userId } from "../../utils/contants";
import useAxios from "../../utils/useAxios";

function Cart() {
  const [cart, setCart] = useState([]);
  const [cartStats, setCartStats] = useState([]);
  const [cartId, setCartId] = useState(() => CartId());
  const [cartCount, setCartCount] = useContext(CartContext);

  const [bioData, setBioData] = useState({
    full_name: "",
    email: "",
    country: "",
  });

  const fetchCartItem = async () => {
    try {
      const response = await apiInstance.get(`course/cart-list/${cartId}/`);
      if (response.data.length === 0) {
        console.log("Cart not found or empty. Resetting cart ID...");
        localStorage.removeItem("randomString"); // Remove old cartId
        const newCartId = CartId(); // Regenerate
        setCartId(newCartId); // Update state
        // Optionally, you can fetch again with new cartId
      } else {
        setCart(response.data);
      }

      await apiInstance.get(`cart/stats/${cartId}/`).then((res) => {
        setCartStats(res.data);
      });
    } catch (error) {
      console.log("Error fetching cart. Resetting cart ID...");
      localStorage.removeItem("randomString");
      const newCartId = CartId();
      setCartId(newCartId);
    }
  };

  useEffect(() => {
    fetchCartItem();
  }, []);

  const navigate = useNavigate();

  const cartItemDelete = async (itemId) => {
    try {
      await apiInstance.delete(`course/cart-item-delete/${cartId}/${itemId}/`);

      // Correct: Update the actual `cart` state
      setCart((prevItems) => prevItems.filter((item) => item.id !== itemId));

      setCartCount((prevCount) => Math.max(prevCount - 1, 0));

      Toast().fire({
        icon: "success",
        title: "Cart Item Deleted",
      });
    } catch (error) {
      console.error("Error deleting cart item:", error);
      Toast().fire({
        icon: "error",
        title: "Failed to delete item",
      });
    }
  };

  const handleBioDataChange = (event) => {
    setBioData({
      ...bioData,
      [event.target.name]: event.target.value,
    });
  };

  const createOrder = async (e) => {
    e.preventDefault();
    if (!bioData.full_name || !bioData.email || !bioData.country) {
      Toast().fire({
        icon: "warning",
        title: "Please provide your bio data",
      });
      return;
    }
    const formdata = new FormData();
    formdata.append("full_name", bioData.full_name);
    formdata.append("email", bioData.email);
    formdata.append("country", bioData.country);
    formdata.append("cart_id", cartId);
    formdata.append("user_id", userId);

    try {
      await useAxios.post(`order/create-order/`, formdata).then((res) => {
        console.log(res.data);
        navigate(`/checkout/${res.data.order_oid}/`);
      });
    } catch (error) {
      console.log(error);
      Toast().fire({
        icon: "error",
        title: error?.response?.data?.detail,
      });
    }
  };

  return (
    <>
      <BaseHeader />

      <section className="py-0">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <div className="bg-light p-4 text-center rounded-3">
                <h1 className="m-0">My cart</h1>
                {/* Breadcrumb */}
                <div className="d-flex justify-content-center">
                  <nav aria-label="breadcrumb">
                    <ol className="breadcrumb breadcrumb-dots mb-0">
                      <li className="breadcrumb-item">
                        <a href="#" className="text-decoration-none text-dark">
                          Home
                        </a>
                      </li>
                      <li className="breadcrumb-item">
                        <a href="#" className="text-decoration-none text-dark">
                          Courses
                        </a>
                      </li>
                      <li
                        className="breadcrumb-item active"
                        aria-current="page"
                      >
                        Cart
                      </li>
                    </ol>
                  </nav>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="pt-5">
        <div className="container">
          <form onSubmit={createOrder}>
            <div className="row g-4 g-sm-5">
              {/* Main content START */}
              <div className="col-lg-8 mb-4 mb-sm-0">
                <div className="p-4 shadow rounded-3">
                  <h5 className="mb-0 mb-3">Cart Items ({cart?.length})</h5>

                  <div className="table-responsive border-0 rounded-3">
                    <table className="table align-middle p-4 mb-0">
                      <tbody className="border-top-2">
                        {cart?.map((c, index) => (
                          <tr>
                            <td>
                              <div className="d-lg-flex align-items-center">
                                <div className="w-100px w-md-80px mb-2 mb-md-0">
                                  <img
                                    src={c.course.image}
                                    style={{
                                      width: "100px",
                                      height: "70px",
                                      objectFit: "cover",
                                    }}
                                    className="rounded"
                                    alt=""
                                  />
                                </div>
                                <h6 className="mb-0 ms-lg-3 mt-2 mt-lg-0">
                                  <a
                                    href="#"
                                    className="text-decoration-none text-dark"
                                  >
                                    {c.course.title}
                                  </a>
                                </h6>
                              </div>
                            </td>
                            <td className="text-center">
                              <h5 className="text-success mb-0">${c.price}</h5>
                            </td>
                            <td>
                              <button
                                onClick={() => cartItemDelete(c.id)}
                                className="btn btn-sm btn-danger px-2 mb-0"
                                type="button"
                              >
                                <i className="fas fa-fw fa-times" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {cart?.length < 1 && (
                      <p className="mt-1 p-1">No Item In Cart</p>
                    )}
                  </div>
                </div>

                {/* Personal info START */}
                <div className="shadow p-4 rounded-3 mt-5">
                  {/* Title */}
                  <h5 className="mb-0">Personal Details</h5>
                  {/* Form START */}
                  <div className="row g-3 mt-0">
                    {/* Name */}
                    <div className="col-md-12 bg-light-input">
                      <label htmlFor="yourName" className="form-label">
                        Your name *
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="yourName"
                        placeholder="Name"
                        name="full_name"
                        value={bioData.full_name}
                        onChange={handleBioDataChange}
                      />
                    </div>
                    {/* Email */}
                    <div className="col-md-12 bg-light-input">
                      <label htmlFor="emailInput" className="form-label">
                        Email address *
                      </label>
                      <input
                        type="email"
                        className="form-control"
                        id="emailInput"
                        placeholder="Email"
                        name="email"
                        value={bioData.email}
                        onChange={handleBioDataChange}
                      />
                    </div>

                    {/* Country option */}
                    <div className="col-md-12 bg-light-input">
                      <label htmlFor="mobileNumber" className="form-label">
                        Select country *
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="mobileNumber"
                        placeholder="Country"
                        name="country"
                        value={bioData.country}
                        onChange={handleBioDataChange}
                      />
                    </div>
                  </div>
                  {/* Form END */}
                </div>
              </div>

              <div className="col-lg-4">
                <div className="p-4 shadow rounded-3">
                  <h4 className="mb-3">Cart Total</h4>
                  <ul class="list-group mb-3">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      Sub Total
                      <span>${cartStats.price?.toFixed(2)}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      Tax
                      <span>${cartStats.tax?.toFixed(2)}</span>
                    </li>
                    <li class="list-group-item d-flex fw-bold justify-content-between align-items-center">
                      Total
                      <span className="fw-bold">
                        ${cartStats.total?.toFixed(2)}
                      </span>
                    </li>
                  </ul>
                  <div className="d-grid">
                    <button type="submit" className="btn btn-lg btn-success">
                      Proceed to Checkout
                    </button>
                  </div>
                  <p className="small mb-0 mt-2 text-center">
                    By proceeding to checkout, you agree to these{" "}
                    <a href="#">
                      {" "}
                      <strong>Terms of Service</strong>
                    </a>
                  </p>
                </div>
              </div>
            </div>
          </form>
        </div>
      </section>

      <BaseFooter />
    </>
  );
}

export default Cart;
