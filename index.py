import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import package_complexity
import flask


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(
            className="container scalable",
            children=[
                html.Div(
                    id="banner",
                    className="banner",
                    children=[
                        html.Img(src=app.get_asset_url("sat_logo.png")),
                        html.H6("SAT"),
                        html.H5(
                            "Reports from 30.08.2019 14:21:14", className="report-date"
                        ),
                    ],
                ),
                dcc.Tabs(
                    id="navigation",
                    value="pcomp",
                    children=[
                        dcc.Tab(label="Package Complexity & Size", value="pcomp"),
                        dcc.Tab(label="Class Complexity & size", value="classcomp"),

                      

                    ],
                ),
                html.Div(id="page-content"),
            ],
        ),
    ]
)


@app.callback(Output("page-content", "children"), [Input("navigation", "value")])
def display_page(tab):
    if tab == "classcomp":
        return html.Div("fuck off")
    elif tab == "pcomp":
        return package_complexity.layout
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=False, threaded=True, processes=1)
