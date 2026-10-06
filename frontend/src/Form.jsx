import { useState } from "react";
import { API } from "./api";

export default function Form({ onCreated }) {
  const [title, setTitle] = useState("");
  const [issuedBy, setIssuedBy] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const data = new FormData();
    data.append("title", title);
    data.append("issued_by", issuedBy);
    data.append("issue_date", issueDate);
    data.append("file", file);

    try {
      const res = await fetch(`${API}/jobs`, { method: "POST", body: data });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(typeof json.detail === "string" ? json.detail : "Please check the form");
      }
      onCreated(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="card" onSubmit={submit}>
      <h2>New certificate job</h2>

      <label>Event / course title</label>
      <input required value={title} onChange={(e) => setTitle(e.target.value)} />

      <label>Issued by</label>
      <input required value={issuedBy} onChange={(e) => setIssuedBy(e.target.value)} />

      <label>Issue date</label>
      <input required type="date" value={issueDate} onChange={(e) => setIssueDate(e.target.value)} />

      <label>Recipients (CSV with a "name" column)</label>
      <input required type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Generate certificates"}
      </button>
    </form>
  );
}
