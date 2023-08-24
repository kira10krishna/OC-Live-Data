
import os
import pandas as pd
file_path = os.path.join("C:\\Users\\kira1\\Documents\\Python Scripts\\Saved data\\Data for 27-Jul-2023", "Nifty_Data_27-Jul-2023.xlsx")
df = pd.read_excel(file_path)

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display



def plot_line_chart(df, strike_price):
    df_filtered = df[df['strikePrice'] == strike_price]

    fig = go.Figure()

    x = df_filtered["Date"]
    fig.add_trace(go.Scatter(x=x, y=df_filtered["lastPrice_CE"], name="Last Price CE", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=x, y=df_filtered["lastPrice_PE"], name="Last Price PE", line=dict(color='red')))

    # Adding secondary Y-axis
    fig.update_layout(yaxis2=dict(anchor="x", overlaying="y", side="right"))
    fig.add_trace(go.Scatter(x=x, y=df_filtered["openInterest_CE"], name="Open Interest CE", line=dict(color='green'), yaxis="y2"))
    fig.add_trace(go.Scatter(x=x, y=df_filtered["openInterest_PE"], name="Open Interest PE", line=dict(color='purple'), yaxis="y2"))
    fig.add_trace(go.Scatter(x=x, y=df_filtered["changeinOpenInterest_CE"], name="Change in OI CE", line=dict(color='orange'), yaxis="y2"))
    fig.add_trace(go.Scatter(x=x, y=df_filtered["changeinOpenInterest_PE"], name="Change in OI PE", line=dict(color='brown'), yaxis="y2"))

    fig.update_layout(title=dict(text="Nifty expiry 27-Jul-2023 for Strike Price: " + str(strike_price),
                                 y=0.95, x=0.5, xanchor='center', yanchor='top'),
                      xaxis_title="Time",
                      yaxis_title="Last Price",
                      yaxis2_title="Open Interest / Change in OI",
                      legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=0.5),
                      showlegend=True,
                      xaxis=dict(
                          rangeslider=dict(
                              visible=True,
                              thickness=0.1,  # Change the thickness of the slider
                              bgcolor="lightgray",  # Change the background color
                              bordercolor="gray"  # Change the border color
                          ),
                          type="date",
                          range=["2023-07-25 09:00:00", "2023-07-25 15:30:00"],  # Set the initial range
                          rangeselector=dict(
                              buttons=list([
                                  dict(count=10, label="Last 10m", step="minute", stepmode="backward"),
                                  dict(count=30, label="Last 30m", step="minute", stepmode="backward"),  # Customize the time intervals
                                  dict(count=1, label="Last 1h", step="hour", stepmode="backward"),
                                  dict(count=2, label="Last 2h", step="hour", stepmode="backward"),
                                  dict(count=3, label="Last 3h", step="hour", stepmode="backward"),
                                  dict(count=6, label="Last 6h", step="hour", stepmode="backward"),
                                  dict(step="all")
                              ]),
                              xanchor='right', x=1 # Align buttons to the right side
                          ),
                          #rangeslider=dict(visible=True, thickness=0.05, bgcolor="#99CCFF"),
                          ticks="outside",  # Place ticks outside the chart
                          ticklen=8,  # Set the length of the ticks
                          tickwidth=2,  # Set the width of the ticks
                          tickcolor="#000"  # Set the color of the ticks
                      ),
                      # Set the adorable background and style
#                       plot_bgcolor="#F7F7F7",  # Light background color
#                       paper_bgcolor="#F7F7F7",  # Light background color for the chart area
                      plot_bgcolor="#E0ECF8",  # Set the background color of the chart area
                      paper_bgcolor="#B0C4DE",  # Set the background color of the paper
                      font=dict(family="Arial", size=12, color="#333")  # Adorable font settings
                      )
    fig.show()
    # fig.write_html('chart.html')


plot_line_chart(df,df.iloc[3,1])