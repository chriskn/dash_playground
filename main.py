from dash.dependencies import Input, Output
import dash
import dash_table
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import figure
import dash_bootstrap_components as dbc

app = dash.Dash("Sat")
app.config.suppress_callback_exceptions = True
app.title = "Sat"

dataframe = pd.read_csv(
    "package_complexity.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python"
)
dataframe = dataframe.drop(columns=["Path"])

table = html.Div(
    id="table",
    className="twelve columns",
    children=dcc.Loading(
        id="tabe-loading",
        children=dash_table.DataTable(
            id="data-table",
            columns=[{"name": i, "id": i} for i in dataframe.columns],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            fill_width=True,
            data=dataframe.to_dict("records"),
            style_header={
                "textTransform": "Uppercase",
                "fontWeight": "bold",
                "backgroundColor": "#ffffff",
                "padding": "10px 0px",
            },
            style_cell={"textAlign": "left"},
            style_data_conditional=[
                {"if": {"row_index": "even"}, "backgroundColor": "#f5f6f7"},
                {"if": {"row_index": "odd"}, "backgroundColor": "#ffffff"},
            ],
        ),
    ),
)

main_content = html.Div(
    className="app_main_content",
    children=[
        html.Details(open=True, className="container scalable", children=[
            html.Summary('Package Complexity & Size', className="summary"),
            html.Div(id="top-row", className="row"),
        ]),
        html.Details(open=True, className="container scalable", children=[
            html.Summary('Number of Methods & Classes', className="summary"),
            html.Div(id="middle-row", className="row"),
        ]),
        html.Div(id="bottom-row", className="row", children=table),
    ],
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
            className="twelve columns",
            children=html.Div(
                [html.H5("Package complexity & size reports from 30.08.2019 14:21:14"), main_content]
            ),
        ),
    ],
)


def _chart(cssClassName="", id="", chart=None):
    return html.Div(className=cssClassName, id=id, children=dcc.Loading(children=chart))


@app.callback(
    Output("top-row", "children"), [Input("data-table", "derived_virtual_data")]
)
def update_top(data):
    data = pd.DataFrame.from_dict(data) if data else dataframe
    return _chart(
        cssClassName="twelve columns",
        id="scatter",
        chart=figure.scatter(
            dataframe=data,
            label_col="Package",
            x_col="Complexity",
            y_col="Number of statements",
            size_col="Average class complexity",
            color_col="Average method complexity",
        ),
    )


@app.callback(
    Output("middle-row", "children"), [Input("data-table", "derived_virtual_data")]
)
def update_middle(data):
    data = pd.DataFrame.from_dict(data) if data else dataframe
    return [
        _chart(
            cssClassName="six columns",
            id="bar1-container",
            chart=figure.barchart(
                title="Number of classes interfaces and enums in package",
                dataframe=data,
                value_col="Number of types",
                label_col="Package",
                max_entries=50,
            ),
        ),
        _chart(
            cssClassName="six columns",
            id="bar2",
            chart=dcc.Loading(
                children=figure.barchart(
                    title="Number of methods in package",
                    dataframe=data,
                    value_col="Number of methods",
                    label_col="Package",
                    max_entries=50,
                )
            ),
        ),
    ]


@app.callback(
    Output("bar2", "hoverData"), [Input("scatter", "hoverData")]
)
def on_scatter_click():
    print("scatter klick")

if __name__ == "__main__":
    app.run_server(debug=True)
