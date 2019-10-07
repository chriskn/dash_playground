import pandas as pd
import urllib.parse as url_parser
from dash.exceptions import PreventUpdate
import constants


def update_download_link(data):
    df = pd.DataFrame.from_dict(data)
    csv_string = df.iloc[:, ::-1].to_csv(index=False, encoding="utf-8", decimal=",")
    csv_string = "data:text/csv;charset=utf-8," + url_parser.quote(csv_string)   
    return csv_string


def update_scatter(selected_indicies, scatter, data):
    chart = scatter
    if selected_indicies:
        fig = chart.figure
        chart.figure = _update_marker(
            selected_indicies, data, fig, fig.data[0].hovertext
        )
    return chart


def update_barchart(
    row_data, selected_indicies, barchart, dataframe, value_cols, label_col, max_entries
):
    chart = barchart
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    if row_data:
        chart.figure = _update_bar_data(
            data, chart.figure, value_cols, label_col, max_entries
        )
    if selected_indicies:
        chart.figure = _update_marker(
            selected_indicies, data, chart.figure, chart.figure.data[0].x
        )
    return chart


def _update_bar_data(data, fig, value_cols, label_col, max_entries):
    labels = list(data[label_col])[:max_entries]
    for i, value_col in enumerate(value_cols):
        fig.data[i].x = labels
        fig.data[i].y = data[value_cols[i]].tolist()[:max_entries]
    fig.data[0].marker = {"color": ["rgb(33,113,181)"] * len(labels)}
    return fig


def _update_marker(selected_indicies, data, figure, graph_labels):
    data_labels = list(data["Package"])
    selected_labels = [data_labels[i] for i in selected_indicies]
    marker_colors = list(figure.data[0].marker.color)
    for i, label in enumerate(graph_labels):
        if label in selected_labels:
            marker_colors[i] = constants.SELECTED_COLOR
    figure.data[0].marker.color = tuple(marker_colors)
    return figure


def get_selected_indicies(table_data, selected_labels):
    packages_in_table = pd.DataFrame.from_dict(table_data)["Package"].tolist()
    indicies = [
        i for i, label in enumerate(packages_in_table) if label in selected_labels
    ]
    return indicies
