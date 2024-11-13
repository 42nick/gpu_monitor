"""Quick visualization of the GPU and CPU usage."""

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

from gpu_monitor.process_handler import DEFAULT_STORING_ROOT


LATEST_CSV = str(sorted(DEFAULT_STORING_ROOT.glob("*.csv"))[-1]) if DEFAULT_STORING_ROOT.exists() else None

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Input(
            id="csv-path",
            type="text",
            placeholder="Enter CSV file path",
        ),
        html.Button("Refresh Data", id="refresh-button"),
        dcc.Graph(id="gpu-memory-usage"),
        dcc.Graph(id="gpu-utilization"),
        dcc.Graph(id="cpu-usage"),
        dcc.Graph(id="memory-usage"),
    ],
)


@app.callback(
    [
        Output("gpu-memory-usage", "figure"),
        Output("gpu-utilization", "figure"),
        Output("cpu-usage", "figure"),
        Output("memory-usage", "figure"),
    ],
    [Input("csv-path", "value"), Input("refresh-button", "n_clicks")],
)
def update_graph(csv_path: str, n_clicks: int) -> tuple[px.line, px.line, px.line, px.line]:
    """Update the graphs based on the CSV file path and the refresh button click."""
    if csv_path and n_clicks:
        df = pd.read_csv(csv_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # GPU Memory Utilization
        fig1 = px.line(df, x="timestamp", y="gpu_0_memory_used", color="gpu_0_name", title="GPU Memory Utilization")

        # GPU Utilization
        fig2 = px.line(df, x="timestamp", y="gpu_0_utilization_gpu", color="gpu_0_name", title="GPU Utilization")

        # Memory Usage
        fig3 = px.line(df, x="timestamp", y="memory_usage", title="Memory Usage")

        # CPU Usage
        fig4 = px.line(df, x="timestamp", y="cpu_usage", title="CPU Usage")

    return fig1, fig2, fig3, fig4


if __name__ == "__main__":
    app.run_server(debug=True)
