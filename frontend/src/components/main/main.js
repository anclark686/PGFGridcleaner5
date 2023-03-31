import React from "react"
import Navbar from "../navbar/navbar";
import Start from "../start/start";

function Main() {
  return (
    <div className="main">
      <Navbar />
      <h1 className="title">GridCleaner 5.0</h1>
      <Start />
    </div>
  );
}

export default Main;
