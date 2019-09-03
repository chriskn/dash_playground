from dash.dependencies import Input, Output
import dash
import dash_table
from datetime import datetime as dt
import dash_core_components as dcc
import package_complexity
import dash_html_components as html
import pandas as pd

app = dash.Dash("SAT")

df = pd.read_csv(
    "package_complexity.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python"
)
PACKAGE_COMP_TAB = package_complexity.content(df)

app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(src=app.get_asset_url("plotly_logo.png")),
                html.H6("SAT"),
            ],
        ),
        html.Div(
            className="twelve columns",
            children=html.Div(
                [
                    html.H5("Reports from 30.08.2019 14:21:14"),
                    dcc.Tabs(
                        id="tabs",
                        value="tab-1",
                        children=[
                            dcc.Tab(label="Package complexity", value="tab-1"),
                            dcc.Tab(label="Tab Two", value="tab-2"),
                        ],
                    ),
                    html.Div(id="tabs-content"),
                ]
            ),
        ),
    ],
)


@app.callback(Output("tabs-content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "tab-1":
        return PACKAGE_COMP_TAB
    elif tab == "tab-2":
        return html.Div(
            [
                html.H3("Tab content 2"),
                dcc.Graph(
                    id="graph-2-tabs",
                    figure={"data": [{"x": [1, 2, 3], "y": [5, 10, 6], "type": "bar"}]},
                ),
            ]
        )


if __name__ == "__main__":
    app.run_server(debug=True)
