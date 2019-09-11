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
import html_components as html_comp
from app import app
from dash.exceptions import PreventUpdate

dataframe = pd.read_csv(
    "package_complexity.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python"
)
dataframe = dataframe.round(2)
id_prefix = "pcomp"


def scatter_plot(data):
    return figure.scatter(
        id=id_prefix + "scatter",
        dataframe=data,
        label_col="Package",
        x_col="Complexity",
        y_col="Number of statements",
        size_col="Average method complexity",
        color_col="Average class complexity",
    )


def barchart1(data):
    return figure.barchart(
        id=id_prefix + "bar1",
        title="Number of classes interfaces and enums in package",
        dataframe=data,
        value_col="Number of types",
        label_col="Package",
        max_entries=50,
    )


def barchart2(data):
    return figure.barchart(
        id=id_prefix + "bar2",
        title="Number of methods in package",
        dataframe=data,
        value_col="Number of methods",
        label_col="Package",
        max_entries=50,
    )


layout = html_comp.three_row_layout(
    row1_children=html_comp.tile(
        class_name="twelve columns", id=id_prefix + "scatter-container"
    ),
    row2_children=[
        html_comp.tile(class_name="six columns", id=id_prefix + "bar1-container"),
        html_comp.tile(class_name="six columns", id=id_prefix + "bar2-container"),
    ],
    row3_children=html_comp.datatable(
        id_prefix=id_prefix,
        dataframe=dataframe,
        hidden_columns=["Path"],
        download_name="package_complexity.csv",
    ),
)


@app.callback(
    Output(id_prefix + "bar1-container", "children"),
    [
        Input(id_prefix + "data-table", "derived_virtual_data"),
        Input(id_prefix + "data-table", "derived_virtual_selected_rows"),
    ],
)
def update_bar1(row_data, selected_indicies):
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    chart = barchart1(data)
    figure = chart.figure
    if selected_indicies:
        chart.figure = update_marked(
            selected_indicies, row_data, figure, figure.data[0].x
        )
    return chart


@app.callback(
    Output(id_prefix + "bar2-container", "children"),
    [
        Input(id_prefix + "data-table", "derived_virtual_data"),
        Input(id_prefix + "data-table", "derived_virtual_selected_rows"),
    ],
)
def update_bar2(row_data, selected_indicies):
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    chart = barchart2(data)
    figure = chart.figure
    if selected_indicies:
        chart.figure = update_marked(
            selected_indicies, row_data, figure, figure.data[0].x
        )
    return chart


@app.callback(
    Output(id_prefix + "scatter-container", "children"),
    [
        Input(id_prefix + "data-table", "derived_virtual_data"),
        Input(id_prefix + "data-table", "derived_virtual_selected_rows"),
    ],
)
def update_scatter(row_data, selected_indicies):
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    chart = scatter_plot(data)
    figure = chart.figure
    if selected_indicies:
        chart.figure = update_marked(
            selected_indicies, row_data, figure, figure.data[0].hovertext
        )
    return chart


@app.callback(
    Output(id_prefix + "download-csv", "href"),
    [Input(id_prefix + "data-table", "derived_virtual_data")],
)
def download_csv(data):
    if data:
        df = pd.DataFrame.from_dict(data)
        csv_string = df.iloc[:, ::-1].to_csv(index=False, encoding="utf-8", decimal=",")
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        return csv_string
    raise PreventUpdate


@app.callback(
    Output(id_prefix + "data-table", "hidden_columns"),
    [Input(id_prefix + "data-table-checkboxes", "value")],
)
def update_hidden_columns(values):
    if not values:
        return ["Path"]
    elif "showPaths" in values:
        return []


@app.callback(
    Output(id_prefix + "data-table", "selected_rows"),
    [
        Input(id_prefix + "data-table-deselect-all", "n_clicks_timestamp"),
        Input(id_prefix + "data-table-deselect-shown", "n_clicks_timestamp"),
        Input(id_prefix + "data-table-select-shown", "n_clicks_timestamp"),
        Input(id_prefix + "scatter", "selectedData"),
        Input(id_prefix + "bar1", "selectedData"),
        Input(id_prefix + "bar2", "selectedData"),
    ],
    state=[
        State(id_prefix + "data-table", "data"),
        State(id_prefix + "data-table", "derived_virtual_data"),
        State(id_prefix + "data-table", "selected_rows"),
    ],
)
def update_selected(
    deselect_all_tst,
    deselect_shown_tst,
    select_shown_tst,
    selected_points,
    selected_bars1,
    selected_bars2,
    table_data,
    filtered_table_data,
    selected_rows,
):
    deselect_shown = int(deselect_shown_tst) if deselect_shown_tst else 0
    select_shown = int(select_shown_tst) if select_shown_tst else 0
    deselect_all = int(deselect_all_tst) if deselect_all_tst else 0
    if selected_bars1:
        selected_labels = [point.get("x") for point in selected_bars1.get("points")]
        return update_selected_table_rows(table_data, selected_labels)
    elif selected_bars2:
        selected_labels = [point.get("x") for point in selected_bars2.get("points")]
        return update_selected_table_rows(table_data, selected_labels)
    elif selected_points:
        selected_labels = [
            point.get("hovertext") for point in selected_points.get("points")
        ]
        return update_selected_table_rows(table_data, selected_labels)
    elif deselect_shown > select_shown and deselect_shown > deselect_all:
        if not selected_rows:
            return []
        labels_to_uncheck = pd.DataFrame.from_dict(filtered_table_data)[
            "Package"
        ].tolist()
        selected_labels = [
            pd.DataFrame.from_dict(table_data)["Package"][i] for i in selected_rows
        ]
        new_selected_labels = [
            selected
            for selected in selected_labels
            if selected not in labels_to_uncheck
        ]
        return update_selected_table_rows(table_data, new_selected_labels)
    elif select_shown > deselect_shown and select_shown > deselect_all:
        selected_labels = pd.DataFrame.from_dict(filtered_table_data)[
            "Package"
        ].tolist()
        return update_selected_table_rows(table_data, selected_labels)
    elif deselect_all > deselect_shown and deselect_all > select_shown:
        return []
    return []


def update_selected_table_rows(table_data, selected_labels):
    packages_in_table = pd.DataFrame.from_dict(table_data)["Package"].tolist()
    indicies = [
        i for i, label in enumerate(packages_in_table) if label in selected_labels
    ]
    return indicies


def update_marked(selected_indicies, row_data, figure, graph_labels):
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    data_labels = list(data["Package"])
    selected_labels = [data_labels[i] for i in selected_indicies]
    marker_colors = list(figure.data[0].marker.color)
    for i, label in enumerate(graph_labels):
        if label in selected_labels:
            marker_colors[i] = "rgb(255, 55, 0)"
    figure.data[0].marker.color = tuple(marker_colors)
    return figure
