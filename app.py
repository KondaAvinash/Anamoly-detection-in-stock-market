from flask import Flask, render_template
import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import yfinance as yf
from stockstats import StockDataFrame as Sdf
from datetime import datetime, timedelta    
import pickle
import random
from dash.dependencies import Input, Output, State

# Flask server setup
server = Flask(__name__)

@server.route('/')
def home():
    return render_template('index.html')

@server.route('/about/')
def about():
    return render_template("about.html")

# Initialize Dash app
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SLATE])

# Dash layout
colors = {"background": "#000000", "text": "#ffFFFF"}

# Try to load tickers.pickle file
try:
    with open("tickers.pickle", "rb") as f:
        ticker_list = pickle.load(f)
except FileNotFoundError:
    print("tickers.pickle not found. Using default tickers.")
    ticker_list = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]  # Default list if file is missing

# Dash Layout
app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.Div([  # header Div
            dbc.Row([ 
                dbc.Col(html.Header([html.H1("Stock Dashboard", style={"textAlign": "center", "color": colors["text"]})]))
            ])
        ]),

        html.Br(), html.Br(), html.Br(), html.Br(),

        html.Div([  # Dropdown Div
            dbc.Row([ 
                dbc.Col(  # Tickers Dropdown
                    dcc.Dropdown(
                        id="stock_name",
                        options=[{"label": str(ticker), "value": str(ticker)} for ticker in ticker_list],
                        searchable=True,
                        value=str(random.choice(ticker_list)),
                        placeholder="Enter stock name",
                    ),
                    width={"size": 3, "offset": 3},
                ),
                dbc.Col(  # Graph Type Dropdown
                    dcc.Dropdown(
                        id="chart",
                        options=[
                            {"label": "Line", "value": "Line"},
                            {"label": "Candlestick", "value": "Candlestick"},
                            {"label": "Simple moving average", "value": "SMA"},
                            {"label": "Exponential moving average", "value": "EMA"},
                            {"label": "MACD", "value": "MACD"},
                            {"label": "RSI", "value": "RSI"},
                            {"label": "OHLC", "value": "OHLC"},
                        ],
                        value="Line",
                        style={"color": "#000000"},
                    ),
                    width={"size": 3},
                ),
                dbc.Col(  # Plot Button
                    dbc.Button("Plot", id="submit-button-state", className="mr-1", n_clicks=0),
                    width={"size": 2},
                ),
            ])
        ]),

        html.Br(), html.Br(), html.Br(),

        html.Div([  # Graphs and DataTable Div
            dbc.Row([ 
                dbc.Col(dcc.Graph(id="live price", config={"displaylogo": False, "modeBarButtonsToRemove": ["pan2d", "lasso2d"]}))
            ]),
            dbc.Row([ 
                dbc.Col(dcc.Graph(id="graph", config={"displaylogo": False, "modeBarButtonsToRemove": ["pan2d", "lasso2d"]}))
            ]),
            dbc.Row([ 
                dbc.Col(dash_table.DataTable(
                    id="info",
                    style_table={"height": "auto"},
                    style_cell={"white_space": "normal", "height": "auto", "backgroundColor": colors["background"], "color": "white", "font_size": "16px"},
                    style_data={"border": "#4d4d4d"},
                    style_header={"backgroundColor": colors["background"], "fontWeight": "bold", "border": "#4d4d4d"},
                    style_cell_conditional=[{"if": {"column_id": c}, "textAlign": "center"} for c in ["attribute", "value"]],
                ), width={"size": 6, "offset": 3})
            ])
        ]),

    ]
)

# Callback for updating graphs
@app.callback(
    [Output("graph", "figure"), Output("live price", "figure")],
    [Input("submit-button-state", "n_clicks")],
    [State("stock_name", "value"), State("chart", "value")]
)
def graph_generator(n_clicks, ticker, chart_name):
    if n_clicks == 0:  # Initial state before button is clicked
        return {}, {}  # Empty figure for now

    # Loading stock data
    print(f"Fetching data for {ticker}...")  # Debugging statement
    start_date = datetime.now().date() - timedelta(days=5 * 365)
    end_date = datetime.now().date()
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d")
    
    # Check if data is fetched
    if df.empty:
        print(f"Error: No data returned for {ticker}.")  # Debugging error
        return {}, {}

    print(f"Data loaded successfully for {ticker}. First few rows:")
    print(df.head())  # Print first few rows of the dataframe for verification

    stock = Sdf(df)

    # Create a live price figure (showing only the most recent price)
    live_price_fig = go.Figure()
    live_price_fig.add_trace(go.Scatter(
        x=[df.index[-1]], y=[df['Close'][-1]], mode='markers+text', text=[f"${df['Close'][-1]:.2f}"],
        textposition="top center", name="Live Price", marker=dict(size=10, color="red")
    ))
    live_price_fig.update_layout(
        title=f"Live Price of {ticker}",
        height=300,
        showlegend=False,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font={"color": colors["text"]}
    )

    # Select graph type
    fig = go.Figure()
    
    if chart_name == "Line":
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], fill="tozeroy", name="Close"))
    elif chart_name == "Candlestick":
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candlestick"))
    elif chart_name == "SMA":
        fig.add_trace(go.Scatter(x=df['Close'].rolling(10).mean().index, y=df['Close'].rolling(10).mean(), name="10 Days"))
        fig.add_trace(go.Scatter(x=df['Close'].rolling(30).mean().index, y=df['Close'].rolling(30).mean(), name="30 Days"))
    elif chart_name == "EMA":
        fig.add_trace(go.Scatter(x=df['Close'].ewm(span=10).mean().index, y=df['Close'].ewm(span=10).mean(), name="10 Days"))
        fig.add_trace(go.Scatter(x=df['Close'].ewm(span=30).mean().index, y=df['Close'].ewm(span=30).mean(), name="30 Days"))
    elif chart_name == "MACD":
        df["MACD"], df["signal"], df["hist"] = stock["macd"], stock["macds"], stock["macdh"]
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD"))
        fig.add_trace(go.Scatter(x=df.index, y=df['signal'], name="Signal"))
        fig.add_trace(go.Scatter(x=df.index, y=df['hist'], line=dict(color="royalblue", width=2, dash="dot"), name="Histogram"))
    elif chart_name == "RSI":
        rsi_6, rsi_12 = stock["rsi_6"], stock["rsi_12"]
        fig.add_trace(go.Scatter(x=df.index, y=rsi_6, name="RSI 6 Day"))
        fig.add_trace(go.Scatter(x=df.index, y=rsi_12, name="RSI 12 Day"))
    elif chart_name == "OHLC":
        fig.add_trace(go.Ohlc(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))

    fig.update_layout(
        height=1000,
        title=chart_name,
        showlegend=True,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font={"color": colors["text"]}
    )
    
    # Update x-axis for range selector and slider
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            activecolor="blue",
            bgcolor=colors["background"],
            buttons=[dict(count=7, label="10D", step="day", stepmode="backward"),
                     dict(count=15, label="15D", step="day", stepmode="backward"),
                     dict(count=1, label="1m", step="month", stepmode="backward"),
                     dict(count=3, label="3m", step="month", stepmode="backward"),
                     dict(count=6, label="6m", step="month", stepmode="backward"),
                     dict(count=1, label="1y", step="year", stepmode="backward")]
        )
    )
    
    return fig, live_price_fig  # Return live price for the first graph and chart for the second graph

# Run the server
if __name__ == '__main__':
    server.run(debug=True)
