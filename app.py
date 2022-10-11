import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from dash.exceptions import PreventUpdate
from plotly import data
from flask_caching import Cache
from utils.services import get_all_stocks, get_stock_from_yahoo

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
cache = Cache(
    app.server,
    config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "./cache", "CACHE_THRESHOLD": 10},
)

# APP LAYOUT
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col([html.Br()])),
        dbc.Row(
            dbc.Col(
                [
                    html.H1("Stonks", className="display-3"),
                    html.Hr(className="my-2"),
                    dcc.Dropdown(id="dropdown"),
                ],
                className="py-3",
                align="center",
            )
        ),
        html.H2(id="stock-name"),
        html.Br(),
        html.H3("Summary"),
        html.P("Lorem Ipsum", id="stock-summary"),
        html.Br(),
        html.H4("Our recommendation"),
        html.P("Lorem Ipsum", id="stock-recommendation"),
        html.Br(),
        html.H3("Stock Chart"),
        dcc.Graph(id="stock-chart"),
        html.Br(),
        html.H3("Indicators"),
        dcc.Graph(id="stock-indicators"),
        html.H3("Social Media Sentiment"),
        dcc.Graph(id="stock-sentiment"),
        html.Br(),
        html.H3("Tweets"),
        html.Br(),
        html.H3("Reddit Posts"),
    ],
    class_name="p-3 bg-light rounded-3",
)


# CACHE FUNCTIONS
# Get list of stock names
@cache.memoize(timeout=60)
def fetch_stock_options() -> list[dict]:
    stocks = get_all_stocks()
    return [{"label": stock.name, "value": stock.ticker} for stock in stocks]


# CALLBACKS FOR INTERACTION
# Main search bar callback
@app.callback(
    Output("dropdown", "options"),
    Input("dropdown", "search_value"),
)
def update_page(search_value):
    if not search_value:
        raise PreventUpdate
    options = [o for o in fetch_stock_options() if search_value in o["label"]]
    if options == []:
        stock = get_stock_from_yahoo(search_value)
        if stock:
            [{"label": stock.name, "value": stock.ticker}]
    return options


# Stock Chart callback
@app.callback(Output("stock-chart", "figure"), Input("dropdown", "value"))
def update_stock_chart(value):
    chart = go.Figure()
    if value:
        # Search result by user
        df = pd.read_csv(
            "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
        )
        chart = go.Figure(
            data=[
                go.Candlestick(
                    x=df["Date"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                )
            ]
        )
    return chart


# Indicators callback
@app.callback(Output("stock-indicators", "figure"), Input("dropdown", "value"))
def update_stock_indicator(value):
    # TODO: Remove this direct dependency on a raw dataset and load from DB/API
    df = data.tips()

    hist = go.Figure(
        go.Histogram2d(
            x=df.total_bill,
            y=df.tip,
            texttemplate="%{z}",
            showscale=False,
            colorscale=["red", "grey", "green"],
            zmax=100,
            zmid=0,
            zmin=-100,
        )
    )
    return hist


# Stock Name callback
@app.callback(Output("stock-name", "children"), Input("dropdown", "value"))
def update_stock_name(value):
    if not value:
        value = "Please pick a stock"
    return value


if __name__ == "__main__":
    app.run_server(debug=True)
