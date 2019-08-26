import os
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash
import dash_table
from datetime import datetime as dt


external_stylesheets = [
    "https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-manufacture-spc-dashboard/assets/base-styles.css"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def createTile(chrildren, classname=None):
    return html.Div(className=classname, children=chrildren)


def heatmap(title):
    return dcc.Graph(
        figure={
            "data": [
                go.Heatmap(
                    x=["1x", "2x", "3x"],
                    y=["1y", "2y", "3y"],
                    z=["2000", "2001", "2002"],
                    colorscale="Reds",
                    colorbar={"title": "Percentage"},
                    showscale=True,
                )
            ],
            "layout": {
                'title': title
            }
        }
    )


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
            className="app_main_content",
            children=[
                html.Div(
                    id="dropdown-select-outer",
                    children=[
                        html.Div(
                            [
                                html.P("Scope"),
                                dcc.Dropdown(
                                    id="dropdown-select",
                                    options=[
                                        {"label": "Projects", "value": "projects"},
                                        {"label": "Packages", "value": "packages"},
                                        {"label": "Classes", "value": "classes"},
                                        {"label": "Methods", "value": "methods"},
                                    ],
                                    value="scope",
                                ),
                            ],
                            className="selector",
                        )
                    ],
                ),
                html.Div(
                    id="top-row",
                    className="row",
                    children=[
                        html.Div(
                            className="four columns",
                            children=dcc.Loading(children=heatmap("Most complex packages")),
                        ),
                        html.Div(
                            className="eight columns",
                            children=dcc.Loading(children=heatmap("Package complexity")),
                        ),
                    ],
                ),
                html.Div(
                    id="middle-row",
                    className="row",
                    children=[
                        html.Div(
                            className="six columns",
                            children=dcc.Loading(children=heatmap("Av. package complexity per class")),
                        ),
                        html.Div(
                            className="six columns",
                            children=dcc.Loading(children=heatmap("Av. package complexity per method")),
                        ),
                    ],
                ),
                html.Div(
                    id="bottom-row",
                    className="row",
                    children=[
                        html.Div(
                            id="flight_info_table_outer",
                            className="twelve columns",
                            children=dcc.Loading(
                                id="table-loading",
                                children=dash_table.DataTable(
                                    id="flights-table",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in [
                                            "flightnum",
                                            "dep_timestamp",
                                            "arr_timestamp",
                                            "origin_city",
                                            "dest_city",
                                        ]
                                    ],
                                    filter_action="native",
                                    fill_width=True,
                                    data=[],
                                    style_as_list_view=True,
                                    style_header={
                                        "textTransform": "Uppercase",
                                        "fontWeight": "bold",
                                        "backgroundColor": "#ffffff",
                                        "padding": "10px 0px",
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "even"},
                                            "backgroundColor": "#f5f6f7",
                                        },
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "#ffffff",
                                        },
                                    ],
                                ),
                            ),
                        )
                    ],
                ),
            ],
        ),
    ],
)

# app.layout = html.Div(
#     children=[
#         html.Header(

#         ),
#         html.H1("Sat"),
#         html.Div(
#             id="container",
#             className="container",
#             children=[
#                 createTile(heatmap(), classname="tile tile2"),
#                 createTile(heatmap(), classname="tile tile3"),
#                 createTile(heatmap(), classname="tile_all"),

#             ],
#         ),
#     ]
# )

if __name__ == "__main__":
    app.run_server(debug=True)
