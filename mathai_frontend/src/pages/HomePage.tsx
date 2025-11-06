import React, { useEffect, useState } from "react";
import { testBackendConnection } from "../services/api";

const HomePage: React.FC = () => {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    testBackendConnection()
      .then(() => setStatus("✅ Backend connected successfully"))
      .catch(() => setStatus("❌ Failed to connect to backend"));
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-indigo-100 to-purple-200 text-gray-900">
      <h1 className="text-4xl font-bold mb-4">MathAI Frontend</h1>
      <p className="text-lg mb-2">Tailwind + React + Vite setup complete</p>
      <p className="text-sm text-gray-700">{status}</p>
    </div>
  );
};

export default HomePage;
