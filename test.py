import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import yahoo_fin.stock_info as yf
import random
import numpy as np
from datetime import datetime, timedelta

# Initialize the app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div(children=[
    html.H1("Stock Data Visualization"),

    html.Div([
        html.Label("Enter Stock Ticker:"),
        dcc.Input(id='ticker', value='AAPL', type='text'),
    ]),

    html.Div([
        html.Label("Enter Chart Name:"),
        dcc.Input(id='chart_name', value='Stock Chart', type='text'),
    ]),

    html.Button(id='submit-button', n_clicks=0, children='Submit'),

    dcc.Graph(id='stock-graph')
])

# Callback function to update the graph
@app.callback(
    Output('stock-graph', 'figure'),
    Input('submit-button', 'n_clicks'),
    State('ticker', 'value'),
    State('chart_name', 'value')
)
def graph_genrator(n_clicks, ticker, chart_name):

    if n_clicks >= 1:  # Checking for user to click submit button

        try:
            # Fetching data for the provided ticker
            start_date = datetime.now().date() - timedelta(days=5 * 365)
            end_date = datetime.now().date()
            df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
            stock = Sdf(df)

            # MITM Attack: Modify stock data
            num_points_to_modify = min(6230, len(df))  # Ensure we do not exceed available data points
            modification_range = 0.05  # The percentage range for modification (e.g., +/- 5%)
            columns_to_modify = ['close']  # Column to modify

            # Step 3: Randomly select rows to modify
            rows_to_modify = sorted(random.sample(range(len(df)), num_points_to_modify))

            # Step 4: Introduce random timing (irregular intervals between modifications)
            random_intervals = np.random.randint(1, 5, size=num_points_to_modify-1)
            rows_to_modify_with_intervals = [rows_to_modify[0]]

            for interval in random_intervals:
                next_row = rows_to_modify_with_intervals[-1] + interval
                if next_row < len(df):
                    rows_to_modify_with_intervals.append(next_row)

            # Step 5: Modify the selected rows with randomized changes
            for row in rows_to_modify_with_intervals:
                for column in columns_to_modify:
                    original_value = df.at[row, column]
                    modification = original_value * random.uniform(-modification_range, modification_range)
                    df.at[row, column] = original_value + modification
            stock = Sdf(df)
            # Creating the graph
            trace = go.Scatter(
                x=df.index,
                y=df['close'],
                mode='lines',
                name=ticker.upper()
            )

            layout = go.Layout(
                title=chart_name,
                xaxis={'title': 'Date'},
                yaxis={'title': 'Closing Price'},
            )

            figure = go.Figure(data=[trace], layout=layout)
            return figure

        except Exception as e:
            # In case of an error (e.g., invalid ticker), return an empty figure
            return go.Figure(
                layout=go.Layout(
                    title=f"Error fetching data for ticker '{ticker}'",
                    xaxis={'title': 'Date'},
                    yaxis={'title': 'Closing Price'},
                )
            )

    return go.Figure()  # Return an empty figure before any clicks

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
