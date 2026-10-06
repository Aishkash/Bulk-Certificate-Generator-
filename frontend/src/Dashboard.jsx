import { useEffect, useState } from "react";
import { API } from "./api";

export default function Dashboard({ job }) {
  const [data, setData] = useState(null);

  // poll every 2s until the job is finished
  useEffect(() => {
    let timer;
    const load = async () => {
      const res = await fetch(`${API}/jobs/${job.job_id}`);
      const json = await res.json();
      setData(json);
      if (!json.status.startsWith("COMPLETED")) timer = setTimeout(load, 2000);
    };
    load();
    return () => clearTimeout(timer);
  }, [job.job_id]);

  if (!data) return <p className="muted">Loading...</p>;

  const done = data.status.startsWith("COMPLETED");

  return (
    <>
      <div className="status-row">
        <h2>{data.title}</h2>
        <span className={`badge ${done ? "done" : "busy"}`}>
          {done ? "Completed" : "Processing..."}
        </span>
      </div>

      <div className="stats">
        <Stat label="Uploaded" value={job.summary.total} />
        <Stat label="Generated" value={data.summary.generated} color="green" />
        <Stat label="Rejected" value={job.rejected.length} color="red" />
        <Stat label="Failed" value={data.summary.failed} color="red" />
        <Stat label="Pending" value={data.summary.pending} />
      </div>

      <div className="card">
        <h3>Certificates</h3>
        {data.certificates.map((c) => (
          <div className="row" key={c.id}>
            <span>{c.name}</span>
            {c.status === "SUCCESS" && (
              <a href={`${API}/certificates/${c.id}/download`}>Download PDF</a>
            )}
            {c.status === "PENDING" && <span className="muted">Generating...</span>}
            {c.status === "FAILED" && <span className="error">{c.error_message}</span>}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Rejected entries ({job.rejected.length})</h3>
        {job.rejected.length === 0 && <p className="muted">None. All names were valid.</p>}
        {job.rejected.map((r, i) => (
          <div className="row" key={i}>
            <span>{r.name || "(empty name)"}</span>
            <span className="error">{r.error}</span>
          </div>
        ))}
      </div>
    </>
  );
}

function Stat({ label, value, color }) {
  return (
    <div className="stat">
      <div className={`num ${color || ""}`}>{value}</div>
      <div className="muted">{label}</div>
    </div>
  );
}