import './css/App.css';

import React, { Fragment } from 'react';
import { Routes, Route } from "react-router-dom";


import Main from './components/main/main';
import Check from './components/check/check';
// import Update from './components/update/update';
// import Email from './components/email/email';

function App() {

  return (
    <div className="app">
      <Fragment >
          <Routes>
            <Route path="/" element={<Main />} />
            {/* <Route path="update" element={<Update />} />
            <Route path="email" element={<Email />} /> */}
            <Route path="check" element={<Check />} />
          </Routes>
      </Fragment>
    </div>
    
  );
}


export default App;
