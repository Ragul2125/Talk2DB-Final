import { LuCloudDownload } from "react-icons/lu";
import { MdOutlineInsertChart } from "react-icons/md";
import { FaEye } from "react-icons/fa";
import downloadCSV from "../../../Services/csv";
import { useRef, useState, useCallback } from "react";
import { GoCopy } from "react-icons/go";
import "./table.css";
import { VscRunBelow } from "react-icons/vsc";
import useApiRequest from "../../../Services/useApiRequest";

const Table = ({ query }) => {
  const { request, loading } = useApiRequest();
  const { request: vreq } = useApiRequest();

  const [data, setData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [showQuery, setShowQuery] = useState(true);
  const [copied, setCopied] = useState(false);
  const [showChartOptions, setShowChartOptions] = useState(false);
  const [showVisualize, setShowVisualize] = useState(false);
  const [visualize, setVisualize] = useState("");
  const [rowCount, setRowCount] = useState(100);
  const [matrix, setMatrix] = useState("0 x 0");
  const [fetchingMore, setFetchingMore] = useState(false);

  const queryEndRef = useRef(null);
  const observer = useRef();

  const handleCopy = () => {
    navigator.clipboard.writeText(query);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleExecute = async () => {
    setFetchingMore(true);
    console.log(rowCount);
    
    const dataResponse = await request("/execute_query", "POST", {
      query: query,
      row_count: rowCount,
    });
    console.log(dataResponse);
    
    if (dataResponse && Array.isArray(dataResponse.results)) {
      setHeaders(Object.keys(dataResponse.results[0]));
      setData(dataResponse.results);
      const rows = dataResponse.results.length;
      const columns = Object.keys(dataResponse.results[0]).length;
      setMatrix(`${rows} x ${columns}`);
    } else {
      console.error("Invalid response from execute_query.");
    }

    setFetchingMore(false);
  };

  const handleVisualize = async (chartType) => {
    if (!chartType) {
      setShowChartOptions((prev) => !prev); // Toggle dropdown
      return;
    }

    setShowChartOptions(false); // Close dropdown after selection
    console.log ("Visualizing with chart type:", chartType);
    const visualize = await vreq("/generate_chart", "POST", {
      query: query,
      num_rows: `${rowCount}`,
      chart_type: chartType, // Pass selected chart type
    });

    if (visualize) {
      setVisualize(visualize.image);
      setShowVisualize(true);
    }
  };

  const lastRowRef = useCallback(
    (node) => {
      if (loading || fetchingMore) return;
      if (observer.current) observer.current.disconnect();

      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && data.length % 100 === 0) {
          setRowCount((prev) => prev + 100);
          handleExecute();
        }
      });

      if (node) observer.current.observe(node);
    },
    [loading, fetchingMore, data]
  );

  return (
    <>
      {showQuery && (
        <div className="query">
          <code className="query-text">{query}</code>
          <button
            title="Copy Query"
            onClick={handleCopy}
            className="copy-button"
          >
            {copied ? "✔" : <GoCopy />}
          </button>
          {!data.length > 0 && (
            <button
              onClick={handleExecute}
              title="Run Query"
              className="copy-button"
            >
              {loading ? <div className="loader" /> : <VscRunBelow />}
            </button>
          )}
          <div ref={queryEndRef} />
        </div>
      )}
      {data.length > 0 && (
        <div className="message bot-message table">
          <div className="table-top">
            <h2>{matrix}</h2>
            <span className="span">
              <LuCloudDownload
                onClick={() => downloadCSV(data, "test.csv")}
                size={20}
                cursor={"pointer"}
                title="Download as CSV"
              />
              <span className="visualize-container">
                <MdOutlineInsertChart
                  size={20}
                  onClick={() => handleVisualize()} // Just toggle the dropdown
                  cursor="pointer"
                  title="Visualize Query"
                />

                {showChartOptions && (
                  <div className="chart-dropdown">
                    <button onClick={() => handleVisualize("bar")}>
                      📊 Bar Chart
                    </button>
                    <button onClick={() => handleVisualize("line")}>
                      📈 Line Chart
                    </button>
                    <button onClick={() => handleVisualize("pie")}>
                      🥧 Pie Chart
                    </button>
                    <button onClick={() => handleVisualize("scatter")}>
                      🔴 Scatter Chart
                    </button>
                  </div>
                )}
              </span>
              <FaEye
                onClick={() => setShowQuery(!showQuery)}
                size={20}
                cursor={"pointer"}
                title="Show Query"
              />
            </span>
          </div>
          <div className="table-wrapper">
            <table className="responsive-table">
              <thead>
                <tr>
                  {headers.map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, index) => (
                  <tr
                    key={index}
                    ref={index === data.length - 1 ? lastRowRef : null}
                  >
                    {headers.map((header) => (
                      <td key={header}>
                        {!row[header] ? "null" : row[header]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {fetchingMore && (
              <div className="fulload">
                <div className="loader" />
              </div>
            )}
          </div>
        </div>
      )}
      {showVisualize && (
        <div className="query">
          <code className="query-text">
            <img
              src={`data:image/png;base64,${visualize}`}
              alt="Visualization"
            />
          </code>
          <div ref={queryEndRef} />
        </div>
      )}
    </>
  );
};

export default Table;
