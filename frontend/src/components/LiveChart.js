import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js';
import createPlotlyComponent from 'react-plotly.js/factory';
import axios from 'axios';

const Plot = createPlotlyComponent(Plotly);

function LiveChart() {
  const [chartData, setChartData] = useState({ x: [], lastPrice_CE: [], lastPrice_PE: [] }); // Initialize with empty data

  useEffect(() => {
    // Function to fetch chart data from the Flask API
    const fetchChartData = async () => {
      try {
        const response = await axios.get(`/api/getChartData?strike_price=${strikePrice}`); // Replace with your API endpoint
        setChartData(response.data);
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    };

    // Call the fetchChartData function when the component mounts
    fetchChartData();
  }, []); // Empty dependency array to run once on component mount

  return (
    <div>
      <h2>Live Chart</h2>
      <Plot
        data={[
          {
            x: chartData.x,
            y: chartData.lastPrice_CE,
            type: 'scatter',
            mode: 'lines',
            name: 'Last Price CE',
            line: { color: 'blue' },
          },
          {
            x: chartData.x,
            y: chartData.lastPrice_PE,
            type: 'scatter',
            mode: 'lines',
            name: 'Last Price PE',
            line: { color: 'red' },
          },
          // Add more traces for other data fields
        ]}
        layout={{
          title: 'Live Chart',
          xaxis: { title: 'Time' },
          yaxis: { title: 'Last Price' },
        }}
      />
    </div>
  );
}

export default LiveChart;
