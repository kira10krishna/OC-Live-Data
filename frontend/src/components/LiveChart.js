import React, { Component, useState, useEffect } from 'react';
import Plotly from 'plotly.js-basic-dist';
import createPlotlyComponent from 'react-plotly.js/factory';
import axios from 'axios';

const Plot = createPlotlyComponent(Plotly);

class LiveChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nf_SP: null,
      df: null,
    };
  }

  componentDidMount() {
    // Fetch nf_SP data from your Flask API
    axios
      .get('/api/strikePrice')
      .then((response) => {
        const nf_SP = response.data.strikePrice;
        this.setState({ nf_SP });
      })
      .catch((error) => {
        console.error('Error fetching nf_SP data:', error);
      });

    // Fetch df data from your Flask API endpoint for df data
    axios
      .get('/api/dfData') // Replace with your Flask API endpoint for df data
      .then((response) => {
        const df = response.data.df;
        // Parse the JSON data into a JavaScript object
        const dfObj = JSON.parse(df);
        this.setState({ df: dfObj.data }); // Assuming your JSON structure has a 'data' field
      })
      .catch((error) => {
        console.error('Error fetching df data:', error);
      });
  }

  render() {
    const { nf_SP, df } = this.state;

    return (
      <div>
        <h1>Live Chart</h1>
        {nf_SP !== null && df !== null ? (
          <Plot
            data={[
              {
                x: df["index"], // Use the appropriate key for x-axis data
                y: df["lastPrice_CE"], // Use the appropriate key for y-axis data
                type: 'scatter',
                mode: 'lines',
                name: 'Last Price CE',
                line: { color: 'blue' },
              },
              {
                x: df["index"], // Use the appropriate key for x-axis data
                y: df["lastPrice_PE"], // Use the appropriate key for y-axis data
                type: 'scatter',
                mode: 'lines',
                name: 'Last Price PE',
                line: { color: 'red' },
              },
              // Add other traces as needed
            ]}
            layout={{
              title: `Nifty expiry 27-Jul-2023 for Strike Price: ${nf_SP}`,
              xaxis: {
                title: 'Time',
                rangeslider: {
                  visible: true,
                  thickness: 0.1,
                  bgcolor: 'lightgray',
                  bordercolor: 'gray',
                },
                type: 'date',
                range: ['2023-07-25 09:00:00', '2023-07-25 15:30:00'],
                rangeselector: {
                  buttons: [
                    { count: 10, label: 'Last 10m', step: 'minute', stepmode: 'backward' },
                    { count: 30, label: 'Last 30m', step: 'minute', stepmode: 'backward' },
                    { count: 1, label: 'Last 1h', step: 'hour', stepmode: 'backward' },
                    // Add other buttons as needed
                  ],
                  xanchor: 'right',
                  x: 1,
                },
                ticks: 'outside',
                ticklen: 8,
                tickwidth: 2,
                tickcolor: '#000',
              },
              yaxis: {
                title: 'Last Price',
              },
              yaxis2: {
                title: 'Open Interest / Change in OI',
                overlaying: 'y',
                side: 'right',
              },
              legend: {
                orientation: 'h',
                yanchor: 'bottom',
                y: 1.01,
                xanchor: 'right',
                x: 0.5,
              },
              plot_bgcolor: '#E0ECF8',
              paper_bgcolor: '#B0C4DE',
              font: { family: 'Arial', size: 12, color: '#333' },
            }}
          />
        ) : (
          <p>Loading chart data...</p>
        )}
      </div>
    );
  }
}

export default LiveChart;
