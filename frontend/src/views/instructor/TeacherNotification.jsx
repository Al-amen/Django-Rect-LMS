import Sidebar from "./Partials/Sidebar";
import Header from "./Partials/Header";
import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";
import { useEffect, useState } from "react";
import useAxios from "../../utils/useAxios";
import UserData from "../plugin/UserData";
import Toast from "../plugin/Toast";
import moment from "moment";

function TeacherNotification() {
  const [noti, setNoti] = useState([]);

  const fetchNoti = () => {
    useAxios.get(`teacher/noti-list/${UserData()?.teacher_id}/`)
    .then((res)=>{
      console.log("Notification",res.data);
      setNoti(res.data);
    });
  };

  useEffect(()=>{
    fetchNoti();
  },[]);

  const handleMarkAsSeen = (notiId) => {
    const formdata = new FormData();

    formdata.append("teacher", UserData()?.teacher_id);
    formdata.append("pk", notiId);
    formdata.append("seen", true);

    useAxios.patch(`teacher/noti-detail/${UserData()?.teacher_id}/${notiId}`, formdata).then((res) => {
        console.log(res.data);
        fetchNoti();
        Toast().fire({
            icon: "success",
            title: "Notication Seen",
        });
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
              <div className="card mb-4">
                {/* Card header */}
                <div className="card-header d-lg-flex align-items-center justify-content-between">
                  <div className="mb-3 mb-lg-0">
                    <h3 className="mb-0">Notifications</h3>
                    <span>Manage all your notifications from here</span>
                  </div>
                </div>
                {/* Card body */}
                <div className="card-body">
                  {/* List group */}
                  <ul className="list-group list-group-flush">
                    {/* List group item */}
                    {noti?.map((n,index)=>(
                      <li key={index} className="list-group-item p-4 shadow rounded-3">
                      <div className="d-flex">
                        <div className="ms-3 mt-2">
                          <div className="d-flex align-items-center justify-content-between">
                            <div>
                              <h4 className="mb-0">{n.type}</h4>
                            </div>
                          </div>
                          <div className="mt-2">
                            <p className="mt-1">
                              <span className="me-2 fw-bold">
                                Date: <span className="fw-light">{ moment(n.date).format("DD MMM, YYYYY")}</span>
                              </span>
                            </p>
                            <p>
                              <button
                                class="btn btn-outline-secondary"
                                type="button"
                              >
                                Mark as Seen <i className="fas fa-check" onClick={() => handleMarkAsSeen(n.id)}></i>
                              </button>
                            </p>
                          </div>
                        </div>
                      </div>
                    </li>
                    ))}
                    
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <BaseFooter />
    </>
  );
}

export default TeacherNotification;
