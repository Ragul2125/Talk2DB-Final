const downloadCSV = (data, filename = "data.csv") => {
  if (!data || !data.length) {
    console.error("No data provided");
    return;
  }

  // Extract headers (keys from the first object)
  const headers = Object.keys(data[0]);
  const csvRows = [];

  // Add header row
  csvRows.push(headers.join(","));

  // Add data rows
  data.forEach((row) => {
    const values = headers.map((header) => {
      let cell = row[header];
      return `"${cell}"`; // Wrap in quotes to handle commas
    });
    csvRows.push(values.join(","));
  });

  // Create a Blob and trigger download
  const csvString = csvRows.join("\n");
  const blob = new Blob([csvString], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

export default downloadCSV;
