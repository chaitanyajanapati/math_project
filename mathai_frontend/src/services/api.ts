export async function testBackendConnection() {
  const response = await fetch("http://127.0.0.1:8000/");
  if (!response.ok) throw new Error("Connection failed");
  return response.json();
}
