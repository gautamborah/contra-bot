import { useEffect, useState } from "react";
import { sayHello } from "./services/api";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const msg = await sayHello();
      setMessage(msg);
    };
    fetchData();
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Contra Costa Knowledge Bot 🧠</h1>
      <p>Backend says: {message}</p>
    </div>
  );
}

export default App;
