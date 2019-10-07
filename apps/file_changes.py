from dash.dependencies import Input, Output, State
import pandas as pd
import figure
import html_components as html_comp
from app import app
from app import cache
from dash.exceptions import PreventUpdate
import controller_common

dataframe = pd.read_csv("file_changes.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python")
dataframe = dataframe.round(2)
id_prefix = "fchanges"
label_col = "File"
value_cols_bar1 = ["Lines added", "Lines removed"]
value_cols_bar2 = ["Number of non fixes", "Number of fixes"]
max_entries_bar = 30

barchart1 = figure.stacked_barchart(
    id=id_prefix + "bar1",
    dataframe=dataframe,
    label_col=label_col,
    sort_col="Changed Lines",
    value_cols=value_cols_bar1,
    marker_colors=["rgb(33,113,181)", "rgb(105,172,233)"],
    max_entries=max_entries_bar,
)


barchart2 = figure.stacked_barchart(
    id=id_prefix + "bar2",
    dataframe=dataframe,
    label_col=label_col,
    sort_col="Number of contributions",
    value_cols=value_cols_bar2,
    marker_colors=["rgb(33,113,181)", "rgb(105,172,233)"],
    max_entries=max_entries_bar,
)

scatter = (
    figure.scatter(
        id=id_prefix + "scatter",
        dataframe=dataframe,
        label_col="File",
        x_col="Changed Lines",
        y_col="Number of lines",
        color_col="Number of contributers",
        size_col="Number of contributions",
    ),
)

layout = html_comp.three_row_layout(
    row1_children=[
        html_comp.tile(
            class_name="twelve columns",
            id=id_prefix + "scatter-container",
            figure=scatter,
        )
    ],
    row2_children=[
        html_comp.tile(
            class_name="six columns", id=id_prefix + "bar-container1", figure=barchart1
        ),
        html_comp.tile(
            class_name="six columns", id=id_prefix + "bar-container2", figure=barchart2
        ),
    ],
    row3_children=html_comp.datatable(
        id_prefix=id_prefix,
        dataframe=dataframe,
        hidden_columns=["Path"],
        download_name="changed_lines_per_file.csv",
    ),
    row1_title="File changes & contributer",
    row2_title="Added and removed lines",
)
