from flask import Flask, render_template
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import plotly.graph_objs as go
import yahoo_fin.stock_info as yf
from stockstats import StockDataFrame as Sdf
from datetime import datetime, timedelta
import pickle
import random
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd


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
colors = {"background": "#000000", "text": "#FFFFFF"}

with open("tickers.pickle", "rb") as f:
    ticker_list = pickle.load(f)

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.Div([  # header Div
            dbc.Row([
                dbc.Col(html.Header([
                    html.H1("Stock Dashboard", style={"textAlign": "center", "color": colors["text"]})
                ]))
            ])
        ]),
        html.Br(), html.Br(), html.Br(), html.Br(),
        html.Div([  # Dropdown Div
            dbc.Row([
                dbc.Col(  # Tickers
                    dcc.Dropdown(
                        id="stock_name",
                        options=[
                            {"label": str(ticker_list[i]), "value": str(ticker_list[i])}
                            for i in range(len(ticker_list))
                        ],
                        searchable=True,
                        value=str(random.choice([
                            "TSLA", "GOOGL", "F", "GE", "AAL", "DIS", "DAL", "AAPL", "MSFT", "CCL", "GPRO", "ACB", "PLUG", "AMZN"
                        ])),
                        placeholder="enter stock name",
                    ),
                    width={"size": 3, "offset": 3},
                ),
                dbc.Col(  # Graph type
                    dcc.Dropdown(
                        id="chart",
                        options=[
                            {"label": "line", "value": "Line"},
                            {"label": "candlestick", "value": "Candlestick"},
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
                dbc.Col(  # button
                    dbc.Button("Plot", id="submit-button-state", className="mr-1", n_clicks=1),
                    width={"size": 2},
                ),
            ])
        ]),
        html.Br(), html.Br(), html.Br(),
        html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id="live price", config={"displaylogo": False, "modeBarButtonsToRemove": ["pan2d", "lasso2d"]}))
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="graph", config={"displaylogo": False, "modeBarButtonsToRemove": ["pan2d", "lasso2d"]}))
            ]),
            dbc.Row([
                dbc.Col(dt.DataTable(
                    id="info",
                    style_table={"height": "auto"},
                    style_cell={"white_space": "normal", "height": "auto", "backgroundColor": colors["background"], "color": "white", "font_size": "16px"},
                    style_data={"border": "#4d4d4d"},
                    style_header={"backgroundColor": colors["background"], "fontWeight": "bold", "border": "#4d4d4d"},
                    style_cell_conditional=[{"if": {"column_id": c}, "textAlign": "center"} for c in ["attribute", "value"]],
                ), width={"size": 6, "offset": 3})
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Button("Buy Stock", id="buy-button", color="success"), width={"size": 2, "offset": 5})
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col(html.Div(id="buy-message", style={"textAlign": "center", "color": colors["text"]}))
            ])
        ]),
        dbc.Modal(
            [
                dbc.ModalHeader("Buy Confirmation"),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal",
            is_open=False,
        )
    ]
)


@app.callback(
    [Output("graph", "figure"), Output("live price", "figure")],
    [Input("submit-button-state", "n_clicks")],
    [State("stock_name", "value"), State("chart", "value")]
)
def graph_generator(n_clicks, ticker, chart_name):

    if n_clicks >= 1:  # Checking for user to click submit button

        start_date = datetime.now().date() - timedelta(days=5 * 365)
        end_date = datetime.now().date()
        df = yf.get_data(ticker, start_date=start_date, end_date=end_date, interval="1d")
        df.close = df.close * 1.1
        stock = Sdf(df)
        # Select graph type

    fig = go.Figure()
    if chart_name == "Line":
        fig.add_trace(go.Scatter(x=list(df.index), y=list(df.close), fill="tozeroy", name="close"))
    elif chart_name == "Candlestick":
        fig.add_trace(go.Candlestick(x=list(df.index), open=list(df.open), high=list(df.high), low=list(df.low), close=list(df.close), name="Candlestick"))
    elif chart_name == "SMA":
        fig.add_trace(go.Scatter(x=list(df.close.rolling(10).mean().index), y=list(df.close.rolling(10).mean()), name="10 Days"))
        fig.add_trace(go.Scatter(x=list(df.close.rolling(15).mean().index), y=list(df.close.rolling(15).mean()), name="15 Days"))
        fig.add_trace(go.Scatter(x=list(df.close.rolling(30).mean().index), y=list(df.close.rolling(30).mean()), name="30 Days"))
        fig.add_trace(go.Scatter(x=list(df.close.rolling(100).mean().index), y=list(df.close.rolling(100).mean()), name="100 Days"))
    elif chart_name == "EMA":
        fig.add_trace(go.Scatter(x=list(df.close.ewm(span=10).mean().index), y=list(df.close.ewm(span=10).mean()), name="10 Days"))
        fig.add_trace(go.Scatter(x=list(df.close.ewm(span=15).mean().index), y=list(df.close.ewm(span=15).mean()), name="15 Days"))
        fig.add_trace(go.Scatter(x=list(df.close.ewm(span=30).mean().index), y=list(df.close.ewm(span=30).mean()), name="30 Days"))
        fig.add_trace(go.Scatter(x=list(df.close.ewm(span=100).mean().index), y=list(df.close.ewm(span=100).mean()), name="100 Days"))
    elif chart_name == "MACD":
        df["MACD"], df["signal"], df["hist"] = stock["macd"], stock["macds"], stock["macdh"]
        fig.add_trace(go.Scatter(x=list(df.index), y=list(df.MACD), name="MACD"))
        fig.add_trace(go.Scatter(x=list(df.index), y=list(df.signal), name="Signal"))
        fig.add_trace(go.Scatter(x=list(df.index), y=list(df.hist), line=dict(color="royalblue", width=2, dash="dot"), name="Histogram"))
    elif chart_name == "RSI":
        rsi_6, rsi_12 = stock["rsi_6"], stock["rsi_12"]
        fig.add_trace(go.Scatter(x=list(df.index), y=list(rsi_6), name="RSI 6 Day"))
        fig.add_trace(go.Scatter(x=list(df.index), y=list(rsi_12), name="RSI 12 Day"))
    elif chart_name == "OHLC":
        fig.add_trace(go.Ohlc(x=df.index, open=df.open, high=df.high, low=df.low, close=df.close))

    fig.update_layout(
        height=1000,
        title=chart_name,
        showlegend=True,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font={"color": colors["text"]}
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            activecolor="green",
            bgcolor="green",
            buttons=list([
                dict(count=30, label="30D", step="day", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(step="all")
            ]),
        )
    )

    live_price = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=df.close[-1],
            number={"prefix": "$"},
            delta={"position": "top", "reference": df.close[-2]},
            title={"text": f"{ticker} Live Price"},
        )
    )
    live_price.update_layout(
        height=200,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font={"color": colors["text"]},
    )

    return fig, live_price


@app.callback(
    [Output("modal", "is_open"), Output("modal-body", "children")],
    [Input("buy-button", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open"), State("stock_name", "value")],
)
def toggle_modal(n1, n2, is_open, stock_name):
    if n1 or n2:
        if not is_open:
            live_price = yf.get_live_price(stock_name)
            modal_body = f"Do you want to buy {stock_name} at ${live_price*1.1:.2f}?"
            return True, modal_body
        return False, ""
    return is_open, ""


if __name__ == "__main__":
    app.run_server(debug=True, port=3000)
