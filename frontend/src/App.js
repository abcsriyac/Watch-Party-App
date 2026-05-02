import React, { useState, useEffect } from "react";
import "./App.css";

function App() {

  // STATE: stores data used across the app
  const [stats, setStats] = useState({}); // Requirement 2: stores report statistics
  const [movies, setMovies] = useState([]); // Requirement 1: supporting table (movies)
  const [users, setUsers] = useState([]); // Requirement 1: supporting table (users)
  const [sessions, setSessions] = useState([]); // Requirement 1 + 2: main table data
  const [editingId, setEditingId] = useState(null); // Requirement 1: tracks edit mode

  // FORM STATE (Requirement 1: ADD/EDIT interface)
  const [form, setForm] = useState({
    movie_id: "",
    host_id: "",
    date: "",
    time: "",
    location: "",
  });

  // FILTER STATE (Requirement 2: report filters)
  const [filterMovie, setFilterMovie] = useState("");
  const [filterHost, setFilterHost] = useState("");
  const [filterStartDate, setFilterStartDate] = useState("");
  const [filterEndDate, setFilterEndDate] = "";

  // Requirement 1: Fetch supporting tables + initial sessions (runs once on page load)
  useEffect(() => {
    fetch("http://127.0.0.1:5000/movies") // supporting table
      .then(res => res.json())
      .then(setMovies);

    fetch("http://127.0.0.1:5000/users") // supporting table
      .then(res => res.json())
      .then(setUsers);

    loadSessions(); // load main table data
  }, []);

  // Requirement 1 + 2: Fetch sessions and report data from backend
  const loadSessions = () => {
    fetch("http://127.0.0.1:5000/sessions/report")
      .then(res => res.json())
      .then(data => {
        setSessions(data.sessions); // populate table
        setStats({ total_sessions: data.stats.total_sessions, filtered: false }); // basic stats
      });
  };

  // Requirement 1: updates form when user types/selects input
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Requirement 1: ADD (POST) and EDIT (PUT)
  const handleSubmit = (e) => {
    e.preventDefault();

    // If editing → update, else → create
    const url = editingId
      ? `http://127.0.0.1:5000/sessions/${editingId}`
      : "http://127.0.0.1:5000/sessions";

    const method = editingId ? "PUT" : "POST";

    // Send data to backend
    fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    })
      .then(res => res.json())
      .then(() => {
        setEditingId(null); // exit edit mode
        resetForm(); // clear form
        loadSessions(); // refresh data
      });
  };

  // Requirement 1: reset form after submit
  const resetForm = () => setForm({
    movie_id: "",
    host_id: "",
    date: "",
    time: "",
    location: ""
  });

  // Requirement 1: EDIT (load existing data into form)
  const handleEdit = (session) => {
    setEditingId(session.session_id); // track which session is being edited
    setForm({
      movie_id: session.movie_id || "",
      host_id: session.host_id || "",
      date: session.date,
      time: session.time,
      location: session.location,
    });
  };

  // Requirement 1: DELETE (remove session)
  const handleDelete = (id) => {
    fetch(`http://127.0.0.1:5000/sessions/${id}`, { method: "DELETE" })
      .then(res => res.json())
      .then(loadSessions); // refresh after delete
  };

  // Requirement 2: Apply filters and generate report
  const applyFilter = () => {

    // validation for date range
    if ((filterStartDate && !filterEndDate) || (!filterStartDate && filterEndDate)) {
      alert("Please select both start and end dates to filter by date.");
      return;
    }

    // build query parameters
    const params = new URLSearchParams();
    if (filterMovie) params.append("movie_id", filterMovie);
    if (filterHost) params.append("host_id", filterHost);
    if (filterStartDate && filterEndDate) {
      params.append("start_date", filterStartDate);
      params.append("end_date", filterEndDate);
    }

    // send request to report endpoint
    fetch(`http://127.0.0.1:5000/sessions/report?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setSessions(data.sessions); // filtered results
        setStats({ ...data.stats, filtered: true }); // detailed stats
      });
  };

  // Requirement 2: Reset filters
  const resetFilter = () => {
    setFilterMovie("");
    setFilterHost("");
    setFilterStartDate("");
    setFilterEndDate("");
    loadSessions();
  };

  return (
    <div className="container">

      {/* UI TITLE */}
      <h1 className="title">👩‍🍳 Watch Party Sessions</h1>

      {/* Requirement 1: ADD + EDIT FORM */}
      <div className="card form-card">
        <h2>{editingId ? "Edit Session" : "Create Session"}</h2>

        <form onSubmit={handleSubmit} className="form">

          {/* Requirement 1: supporting table dropdown (movies) */}
          <select name="movie_id" value={form.movie_id} onChange={handleChange} required>
            <option value="">Select Movie</option>
            {movies.map(m => (
              <option key={m.movie_id} value={m.movie_id}>{m.title}</option>
            ))}
          </select>

          {/* Requirement 1: supporting table dropdown (users) */}
          <select name="host_id" value={form.host_id} onChange={handleChange} required>
            <option value="">Select Host</option>
            {users.map(u => (
              <option key={u.user_id} value={u.user_id}>{u.name}</option>
            ))}
          </select>

          {/* Requirement 1: form inputs */}
          <input type="date" name="date" value={form.date} onChange={handleChange} required />
          <input type="time" name="time" value={form.time} onChange={handleChange} required />
          <input type="text" name="location" placeholder="Location" value={form.location} onChange={handleChange} />

          {/* Requirement 1: submit button */}
          <button type="submit">
            {editingId ? "Update Session" : "Add Session"}
          </button>
        </form>
      </div>

      {/* Requirement 2: FILTER INTERFACE */}
      <div className="card filter-card">
        <h2>🔍 Filter Sessions</h2>

        <div className="form">

          {/* filter by movie */}
          <select value={filterMovie} onChange={e => setFilterMovie(e.target.value)}>
            <option value="">All Movies</option>
            {movies.map(m => <option key={m.movie_id} value={m.movie_id}>{m.title}</option>)}
          </select>

          {/* filter by host */}
          <select value={filterHost} onChange={e => setFilterHost(e.target.value)}>
            <option value="">All Hosts</option>
            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
          </select>

          {/* filter by date range */}
          <input type="date" value={filterStartDate} onChange={e => setFilterStartDate(e.target.value)} />
          <input type="date" value={filterEndDate} onChange={e => setFilterEndDate(e.target.value)} />

          {/* apply/reset filters */}
          <button onClick={applyFilter}>Apply Filter</button>
          <button onClick={resetFilter}>Reset Filter</button>
        </div>
      </div>

      {/* Requirement 2: REPORT + STATISTICS */}
      <div className="card stats-card">
        <h2>📊 Sessions Report</h2>

        {/* always show total */}
        <p>Total Sessions: {stats.total_sessions || 0}</p>

        {/* show detailed stats only when filtered */}
        {stats.filtered && (
          <>
            <p>Average Duration: {stats.average_duration}</p>

            <div>
              <strong>Sessions per Movie:</strong>
              {stats.sessions_per_movie &&
                Object.entries(stats.sessions_per_movie).map(([movie, count]) => (
                  <p key={movie}>{movie}: {count}</p>
                ))}
            </div>

            <div>
              <strong>Sessions per Host:</strong>
              {stats.sessions_per_host &&
                Object.entries(stats.sessions_per_host).map(([host, count]) => (
                  <p key={host}>{host}: {count}</p>
                ))}
            </div>
          </>
        )}
      </div>

      {/* Requirement 1 + 2: TABLE DISPLAY */}
      <div className="card table-card">
        <h2>📋 Sessions Report</h2>

        <table>
          <thead>
            <tr>
              <th>Movie</th>
              <th>Host</th>
              <th>Date</th>
              <th>Time</th>
              <th>Location</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {sessions.map(s => (
              <tr key={s.session_id}>
                <td>{s.movie}</td>
                <td>{s.host}</td>
                <td>{s.date}</td>
                <td>{s.time}</td>
                <td>{s.location}</td>

                <td>
                  {/* Requirement 1: EDIT button */}
                  <button onClick={() => handleEdit(s)}>Edit</button>

                  {/* Requirement 1: DELETE button */}
                  <button onClick={() => handleDelete(s.session_id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default App;