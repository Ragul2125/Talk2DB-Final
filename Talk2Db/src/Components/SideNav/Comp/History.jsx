import React, { useEffect } from "react";
import "../SideNav.css";
import { PiDotsThreeOutlineFill } from "react-icons/pi";
import useApiRequest from "../../../Services/useApiRequest";
import { useNavigate, useParams } from "react-router-dom";
const History = () => {
  const { id } = useParams();
  const { request, loading, error, data: history } = useApiRequest();
  const navigate = useNavigate();
  useEffect(() => {
    const func = async () => {
      await request("/conversation_history", "GET");
    };
    func();
  }, [id]);

  return (
    <>
      {history?.length > 0 &&
        history.map((item, index) => (
          <div className="history" key={index}>
            <div className="history-title">
              <h4>{item.title}</h4>
            </div>
            <div className="history-area">
              <div className="historys">
                {item.historys.map((items, idx) => (
                  <div
                    className={"row " + (items.id == id ? "active" : "")}
                    onClick={() => {
                      navigate(`/home/${items.id}`);
                    }}
                    key={idx}
                  >
                    <p>{items.history}...</p>
                    <PiDotsThreeOutlineFill />
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
    </>
  );
};

export default History;
