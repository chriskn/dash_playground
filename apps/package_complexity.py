from dash.dependencies import Input, Output, State
import dash
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import figure
import dash_bootstrap_components as dbc
import urllib
import html_components as hmtl_comp
from app import app

dataframe = pd.read_csv(
    "package_complexity.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python"
)
dataframe= dataframe.round(2)
#dataframe = dataframe.drop(columns=["Path"])







def _tile(cssClassName="", id="", chart=None):
    return html.Div(className=cssClassName, children=dcc.Loading(id=id, children=chart))


def scatter_plot(data):
    return _tile(
        cssClassName="twelve columns",
        id="scatter-container",
        chart=figure.scatter(
            id="scatter",
            dataframe=data,
            label_col="Package",
            x_col="Complexity",
            y_col="Number of statements",
            size_col="Average method complexity",
            color_col="Average class complexity",
        ),
    )


def barchart1(data):
    return _tile(
        cssClassName="six columns",
        id="bar1-container",
        chart=figure.barchart(
            id="bar1",
            title="Number of classes interfaces and enums in package",
            dataframe=data,
            value_col="Number of types",
            label_col="Package",
            max_entries=50,
        ),
    )


def barchart2(data):
    return _tile(
        cssClassName="six columns",
        id="bar2-container",
        chart=figure.barchart(
            id="bar2",
            title="Number of methods in package",
            dataframe=data,
            value_col="Number of methods",
            label_col="Package",
            max_entries=50,
        ),
    )

table = hmtl_comp.datatable(dataframe=dataframe, hidden_columns=["Path"], download_name="package_complexity.csv")


layout = html.Div(
    className="app_main_content",
    children=[
        html.Details(
            open=True,
            className="container scalable",
            children=[
                html.Summary("Package Complexity & Size", className="summary"),
                html.Div(
                    id="top-row", className="row", children=scatter_plot(dataframe)
                ),
            ],
        ),
        html.Details(
            open=True,
            className="container scalable",
            children=[
                html.Summary("Number of Methods & Classes", className="summary"),
                html.Div(
                    id="middle-row",
                    className="row",
                    children=[barchart1(dataframe), barchart2(dataframe)],
                ),
            ],
        ),
        html.Div(id="bottom-row", className="row", children=table),
    ],
)


@app.callback(
    Output("top-row", "children"),
    [
        Input("data-table", "derived_virtual_data"),
        Input("data-table", "derived_virtual_selected_rows"),
    ],
)
def update_top(filter_data, selected_indicies):
    data = pd.DataFrame.from_dict(filter_data) if filter_data else dataframe
    return scatter_plot(data)


@app.callback(
    Output("middle-row", "children"),
    [
        Input("data-table", "derived_virtual_data"),
        Input("data-table", "derived_virtual_selected_rows"),
    ],
)
def update_middle(filter_data, selected_indicies):
    data = pd.DataFrame.from_dict(filter_data) if filter_data else dataframe
    return [barchart1(data), barchart2(data)]


@app.callback(
    Output("scatter", "figure"),
    [
        Input("data-table", "derived_virtual_selected_rows"),
        Input("data-table", "derived_virtual_data"),
    ],
    state=[State("scatter", "figure")],
)
def update_scatter(selected_indicies, row_data, figure):
    if selected_indicies:
        return update_marked(
            selected_indicies, row_data, figure, figure.get("data")[0].get("hovertext")
        )
    return figure


@app.callback(
    Output("bar2", "figure"),
    [
        Input("data-table", "derived_virtual_selected_rows"),
        Input("data-table", "derived_virtual_data"),
    ],
    state=[State("bar2", "figure")],
)
def update_bar2(selected_indicies, row_data, figure):
    if selected_indicies:
        return update_marked(
            selected_indicies, row_data, figure, figure.get("data")[0].get("x")
        )
    return figure


@app.callback(
    Output("bar1", "figure"),
    [
        Input("data-table", "derived_virtual_selected_rows"),
        Input("data-table", "derived_virtual_data"),
    ],
    state=[State("bar1", "figure")],
)
def update_bar1(selected_indicies, row_data, figure):
    if selected_indicies:
        return update_marked(
            selected_indicies, row_data, figure, figure.get("data")[0].get("x")
        )
    return figure

@app.callback(Output("download-csv", "href"), [Input("data-table", "derived_virtual_data")])
def download_csv(data):
    if data:
        df = pd.DataFrame.from_dict(data)
        csv_string = df.iloc[:, ::-1].to_csv(index=False, encoding='utf-8', decimal=",")
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        return csv_string

@app.callback(
    Output("data-table", "selected_rows"),
    [
        Input("scatter", "selectedData"),
        Input("bar1", "selectedData"),
        Input("bar2", "selectedData"),

    ],
    state=[State("data-table", "data")],

)
def update_selected(selected_points, selected_bars1,selected_bars2,  table_data):
    if selected_bars1:
        selected_labels = [point.get("x") for point in selected_bars1.get("points")]
        return update_selected_table_rows(table_data, selected_labels)
    if selected_bars2:
        selected_labels = [point.get("x") for point in selected_bars2.get("points")]
        return update_selected_table_rows(table_data, selected_labels)
    if selected_points:
        selected_labels = [point.get("hovertext") for point in selected_points.get("points")]
        return update_selected_table_rows(table_data, selected_labels)
    return []

def update_selected_table_rows(table_data, selected_labels):
        packages_in_table = pd.DataFrame.from_dict(table_data)["Package"].tolist()
        indicies = [i for i, label in enumerate(packages_in_table) if label in selected_labels]
        return indicies

def update_marked(selected_indicies, row_data, figure, graph_labels):
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    data_labels = list(data["Package"])
    selected_labels = [data_labels[i] for i in selected_indicies]
    marker_colors = figure.get("data")[0].get("marker").get("color")
    for i, label in enumerate(graph_labels):
        if label in selected_labels:
            marker_colors[i] = "rgb(255, 55, 0)"
    figure.get("data")[0].get("marker")["color"] = marker_colors
    return figure


