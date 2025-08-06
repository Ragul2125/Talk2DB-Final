import { useState } from "react";
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000"; // Set your static base URL here

const useApiRequest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const request = async (
    endpoint,
    method = "GET",
    body = null,
    headers = {}
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios({
        url: `${BASE_URL}${endpoint}`,
        method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
        data: body,
      });
      console.log(response.data);
      setData(response.data);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { request, loading, error, data };
};

export default useApiRequest;

// Usage Example:
// const { request, loading, error, data } = useApiRequest();
// useEffect(() => {
//   request("/users", "GET").then(data => console.log(data));
// }, []);
