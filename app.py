import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, html
from dash.exceptions import PreventUpdate

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

def create_card(data):
    body_text = "Sample text."

    ri_card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Sample Card", className="card-title"),
                    html.P(body_text, className="card-text"),
                ]
            )
        ]
    )
    return ri_card


jumbotron = html.Div(
    dbc.Col(
        [
            html.H1("Header", className="display-3"),
            html.Hr(className="my-2"),
            dbc.Input(id="input", placeholder="Search...", type="text", debounce=True),
        ],
        className="py-3",
    ),
)


# CALLBACKS FOR INTERACTION
# Main search bar callback
@app.callback(
    [
        Output("output_title", "children"),
        Output("card1", "children"),
        Output("card2", "children"),
        Output("card3", "children"),
    ],
    [Input("input", "value")],
)
def update_page(search_term):
    if search_term in [None, ""]:
        raise PreventUpdate
    else:
        card1 = create_card(search_term)
        card2 = create_card(search_term)
        card3 = create_card(search_term)
        return search_term, card1, card2, card3


# APP LAYOUT
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col([html.Br()])),
        dbc.Row(jumbotron),
        dbc.Row([dbc.Col(html.H1(id="output_title"))]),
        dbc.Row([dbc.Col([html.Div(id="card1")]), dbc.Col([html.Div(id="card2")])]),
        dbc.Row(dbc.Col([html.Br()])),
        dbc.Row([dbc.Col([html.Div(id="card3")])]),
    ],
    class_name="p-3 bg-light rounded-3",
)

if __name__ == "__main__":
    app.run_server(debug=True)
