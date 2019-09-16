import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, cache
from apps import package_complexity
from apps import class_complexity
import flask
from dash.exceptions import PreventUpdate
import re

navigation = html.Div(
    className="topnav",
    id="topnav",
    children=[
        dcc.Link(
            "Package Complexity & Size",
            id="packcomp",
            className="navigation-link",
            href="/sat/packcomp",
        ),
        dcc.Link(
            "Class Complexity & size",
            className="navigation-link",
            href="/sat/classcomp",
        ),
    ],
)

default_page = "/sat/packcomp"


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
                navigation,
                # dcc.Tabs(
                #     id="navigation",
                #     value="pcomp",
                #     children=[
                #         dcc.Tab(label="Package Complexity & Size", value="packcomp"),
                #         dcc.Tab(label="Class Complexity & size", value="classcomp"),
                #     ],
                # ),
                html.Div(id="page-content"),
            ],
        ),
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
@cache.memoize()
def display_tab_content(path):
    if path == "/sat/classcomp":
        return class_complexity.layout
    elif path == "/sat/packcomp":
        return package_complexity.layout
    else:
        return package_complexity.layout


@app.callback(Output("topnav", "children"), [Input("url", "pathname")])
def highlight_tab(path):
    is_valid_link = path in [link.href for link in navigation.children]
    for link in navigation.children:
        is_default = not path or (not is_valid_link and link.href == default_page)
        if link.href == path:
            link.className = "topnav-selected"
        elif is_default:
            link.className = "topnav-selected"
        else:
            link.className = "topnav"
    return navigation.children


if __name__ == "__main__":
    app.run_server(debug=True)
