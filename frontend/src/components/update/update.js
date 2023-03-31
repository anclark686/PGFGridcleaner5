import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'
import Navbar from "./navbar/navbar";
import { post } from 'utils/requests';
import { Spinner } from "react-bootstrap";

function Update() {
    const [loading, setLoading] = useState(false);

    let data = useLocation();
    const masterNum = data.state.masterNum;
    const details = data.state.details

    const navigate = useNavigate();
    
    const updatePC = async () => {
        setLoading(true);

        await post(
            [masterNum, details], // Body
            'update', // Route
            (res) => {
            setLoading(false);
            console.log(masterNum)
            console.log(details)
            }, // Response callback
            (error) => console.error(error) // Error callback
        )
    }

    useEffect(() => {
      updatePC()
      console.log(details)
    }, [])
    
    const goToEmail = () => {
        navigate("/email", { state: { 
            masterNum: masterNum,
            details: details
          } });
    }

    return(
        <div className='update'>
            <Navbar />

            <h1>Update</h1>
            {!loading ? (
                <>
                    <h4>PC has been updated! (Feel free to check)</h4>
                    <button className="btn btn-info btn-lg" onClick={() => goToEmail()}>
                        Send Emails
                    </button>
                </>
            ) 
            : 
            <>
                <h4>Updating PC...</h4>
                <Spinner animation="border" variant="info" />
            </>
            }
        </div>
    )
}

export default Update;