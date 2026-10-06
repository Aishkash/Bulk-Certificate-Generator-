
import { useState } from "react";
import Form from "./Form";
import Dashboard from "./Dashboard";

export default function App() {
  const [job, setJob] = useState(null); // response of POST /jobs

  return (
    <div className="app">
      <header>
        <h1>Certificate Generator</h1>
        {job && (
          <button className="ghost" onClick={() => setJob(null)}>
            + New job
          </button>
        )}
      </header>
      {job ? <Dashboard job={job} /> : <Form onCreated={setJob} />}
    </div>
  );
}
