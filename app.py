import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from dash.exceptions import PreventUpdate
from plotly import data

# TODO: Remove once database is connected to this page
options = [
    {"label": "New York City", "value": "NYC"},
    {"label": "Montreal", "value": "MTL"},
    {"label": "San Francisco", "value": "SF"},
]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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


# CALLBACKS FOR INTERACTION
# Main search bar callback
@app.callback(
    Output("dropdown", "options"),
    Input("dropdown", "search_value"),
)
def update_page(search_value):
    if not search_value:
        raise PreventUpdate
    # Replace o["label"] with a database query
    return [o for o in options if search_value in o["label"]]


# Stock Chart callback
@app.callback(Output("stock-chart", "figure"), Input("dropdown", "value"))
def update_stock_chart(value):
    # TODO: Remove this direct dependency on a raw dataset and load from DB/API
    if value:
        # Search result by user
        df = pd.read_csv(
            "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
        )
    else:
        # Display S&P 500 chart
        value = "S&P 500"
        df = pd.read_csv(
            "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
        )
    chart = go.Figure(
        data=[
            go.Candlestick(
                x=df["Date"],
                open=df["AAPL.Open"],
                high=df["AAPL.High"],
                low=df["AAPL.Low"],
                close=df["AAPL.Close"],
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
        value = "S&P 500"
    return value


if __name__ == "__main__":
    app.run_server(debug=True)
