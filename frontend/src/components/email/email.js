import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import Navbar from "components/navbar/navbar";
import { get } from "utils/requests";
import { Spinner, Modal } from "react-bootstrap";

function Email() {
  const [loading, setLoading] = useState(false);
  const [show, setShow] = useState(false);
  const [email, setEmail] = useState("");

  let data = useLocation();
  const masterNum = data.state.masterNum;
  const details = data.state.details;

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  const sendEmails = async () => {
    setLoading(true);

    await get(
      "email", // Route
      (res) => {
        setLoading(false);
      }, // Response callback
      (error) => console.error(error) // Error callback
    );
  };

  const generateEmail = () => {
    const add = Number(details.stats["rsps_to_add"]);
    const del = Number(details.stats["rsps_to_delete"]);
    const change = Number(details.stats["rsps_to_change"]);
    const greeting = "Hi, \nThank you for your update! I can confirm that ";
    let message = "";
    let addMess =
      add > 1
        ? `${add} new respondents have been added`
        : `${add} new respondent has been added`;
    let delMess =
      del > 1
        ? `${del} respondents have been removed.`
        : `${del} respondent has been removed.`;
    let changeMess =
      change > 1
        ? `${change} respondents have been adjusted`
        : `${change} respondent has been adjusted`;
    let haveHas = add + change > 1 ? "invites have been" : "invite has been";

    if (add && del && change) {
      message = `${addMess}, ${changeMess} and their ${haveHas}. I can also confirm that ${del}.`;
    } else if (add && del) {
      message = `${addMess}, and their ${haveHas}. I can also confirm that ${del}.`;
    } else if (add && change) {
      message = `${addMess}, ${changeMess} and their ${haveHas}.`;
    } else if (change && del) {
      message = `${changeMess} and their ${haveHas}. I can also confirm that ${del}.`;
    } else if (add) {
      message = `${addMess}, and their ${haveHas}.`;
    } else if (del) {
      message = delMess;
    } else if (change) {
      message = `${changeMess} and their ${haveHas}.`;
    }

    return greeting + message;
  };

  useEffect(() => {
    sendEmails();
    setEmail(generateEmail());
    console.log(details);
  }, []);

  return (
    <div className="email">
      <Navbar />
      <h1>Email</h1>
      {!loading ? (
        <>
          <h4>Emails Have been sent! </h4>

          <button onClick={handleShow} className="btn btn-info btn-lg">
            Generate Email
          </button>

          <Modal show={show} onHide={handleClose} animation={false}>
            <Modal.Header closeButton>
              <Modal.Title>Email to RCR</Modal.Title>
            </Modal.Header>
            <Modal.Body>{email}</Modal.Body>
            <Modal.Footer>
              <button className="btn btn-info btn-lg" onClick={handleClose}>
                Close
              </button>
              <button onClick={() => navigator.clipboard.writeText({ email })}>
                Copy
              </button>
            </Modal.Footer>
          </Modal>

          <Link to="/">
            <button className="btn btn-info btn-lg">Start Over</button>
          </Link>
        </>
      ) : (
        <>
          <h4>Sending Emails...</h4>
          <Spinner animation="border" variant="info" />
        </>
      )}
    </div>
  );
}

export default Email;
