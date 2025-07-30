import React, { useContext, useEffect, useState } from 'react'
import BaseHeader from '../partials/BaseHeader'
import BaseFooter from '../partials/BaseFooter'
import Sidebar from './Partials/Sidebar'
import Header from './Partials/Header'
import useAxios from '../../utils/useAxios';
import UserData from '../plugin/UserData'
import Toast from '../plugin/Toast';
import { ProfileContext } from '../plugin/Context'

function Profile() {
  const [profile,setProfile] = useContext(ProfileContext)
  const [profileData,setProfileData] = useState({
    image:'',
    full_name: '',
    about: '',
    country: ''
  });
  const [imagePreview, setImagePreview] = useState("");

  const fetchProfile = () => {
    useAxios.get(`user/profile/${UserData()?.user_id}/`)
    .then((res)=>{
      setProfileData(res.data);
      setProfile(res.data);
      setImagePreview(res.data.image);
    });
  };

  useEffect(()=>{
    fetchProfile();
  },[]);

  const handleProfileChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e)=>{
    const seletedFile = e.target.files[0];
    setProfileData({
      ...profileData,
      [e.target.name]: seletedFile,
    });
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    if(seletedFile) {
      reader.readAsDataURL(seletedFile);
    }

  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();

    const res = await useAxios.get(`user/profile/${UserData()?.user_id}/`);
    const formdata = new FormData();
    if (profileData.image && profileData.image !== res.data.image) {
        formdata.append("image", profileData.image);
    }

    formdata.append("full_name", profileData.full_name);
    formdata.append("about", profileData.about);
    formdata.append("country", profileData.country);

    await useAxios
        .patch(`user/profile/${UserData()?.user_id}/`, formdata, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        })
        .then((res) => {
            console.log(res.data);
            setProfile(res.data);
            fetchProfile(); // Refresh profile data
            Toast().fire({
              icon: "success",
              title: "Profile updated successfully",
            });
           // setProfile(res.data);
        });
};
 

  return (
    <>
      <BaseHeader />

      <section className="pt-5 pb-5">
        <div className="container">
          {/* Header Here */}
          <Header />
          <div className="row mt-0 mt-md-4">
            {/* Sidebar Here */}
            <Sidebar />
            <div className="col-lg-9 col-md-8 col-12">
              {/* Card */}
              <div className="card">
                {/* Card header */}
                <div className="card-header">
                  <h3 className="mb-0">Profile Details</h3>
                  <p className="mb-0">
                    You have full control to manage your own account setting.
                  </p>
                </div>
                {/* Card body */}
                <form onSubmit={handleFormSubmit} className="card-body">
                  <div className="d-lg-flex align-items-center justify-content-between">
                    <div className="d-flex align-items-center mb-4 mb-lg-0">
                      <img
                        src={imagePreview || "https://via.placeholder.com/100"}
                        id="img-uploaded"
                        className="avatar-xl rounded-circle"
                        alt="avatar"
                        style={{ width: "100px", height: "100px", borderRadius: "50%", objectFit: "cover" }}
                      />
                      <div className="ms-3">
                        <h4 className="mb-0">Your avatar</h4>
                        <p className="mb-0">
                          PNG or JPG no bigger than 800px wide and tall.
                        </p>
                        <input type="file" className='form-control mt-3' name='image' id="" onChange={handleFileChange} />
                      </div>
                    </div>
                  </div>
                  <hr className="my-5" />
                  <div>
                    <h4 className="mb-0">Personal Details</h4>
                    <p className="mb-4">Edit your personal information and address.</p>
                    {/* Form */}
                    <div className="row gx-3">
                      {/* First name */}
                      <div className="mb-3 col-12 col-md-12">
                        <label className="form-label" htmlFor="fname">
                          Full Name
                        </label>
                        <input
                          type="text"
                          id="fname"
                          className="form-control"
                          placeholder="First Name"
                          required=""
                          value={profileData.full_name || ""}
                          name='full_name'
                          onChange={handleProfileChange}
                        />
                        <div className="invalid-feedback">Please enter first name.</div>
                      </div>
                      {/* Last name */}
                      <div className="mb-3 col-12 col-md-12">
                        <label className="form-label" htmlFor="lname">
                          About Me
                        </label>
                        <textarea name="about" id="" cols="30" rows="5" className='form-control' value={profileData.about} onChange={handleProfileChange}  ></textarea>
                        <div className="invalid-feedback">Please enter last name.</div>
                      </div>

                      {/* Country */}
                      <div className="mb-3 col-12 col-md-12">
                        <label className="form-label" htmlFor="editCountry">
                          Country
                        </label>
                        <input
                          type="text"
                          id="country"
                          className="form-control"
                          placeholder="Country"
                          required=""
                          value={profileData.country || ""}
                          name='country'
                          onChange={handleProfileChange}
                        />
                        <div className="invalid-feedback">Please choose country.</div>
                      </div>
                      <div className="col-12">
                        {/* Button */}
                        <button className="btn btn-primary" type="submit">
                          Update Profile <i className='fas fa-check-circle'></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </form>
              </div>
            </div>

          </div>
        </div>
      </section>

      <BaseFooter />
    </>
  )
}

export default Profile