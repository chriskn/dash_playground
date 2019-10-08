from dash.dependencies import Input, Output, State
import pandas as pd
import figure
import html_components as html_comp
import datatable_common as table_common
from app import app
from app import cache
from dash.exceptions import PreventUpdate
import controller_common
import time
import plotly.express as px
import constants
import dash_html_components as html
import math
import dash

dataframe = pd.read_csv(
    "package_complexity.csv",
    sep=";",
    decimal=",",
    header=0,
    encoding="ascii",
    engine="python",
)


id_prefix = "pcomp"
dataframe.columns = [
    "Package",
    "Complexity",
    "Num. statements",
    "Num. classes",
    "Num. abstract classes",
    "Num. interfaces",
    "Num. enums",
    "Num. types",
    "Num. methods",
    "Av. class complexity",
    "Av. method complexity",
    "Project",
    "Path",
]
hidden_columns = [
    "Num. classes",
    "Num. abstract classes",
    "Num. interfaces",
    "Num. enums",
    "Project",
    "Path",
]
value_cols_bar2 = ["Num. methods"]
value_cols_bar1 = [
    "Num. classes",
    "Num. abstract classes",
    "Num. interfaces",
    "Num. enums",
]
label_col = "Package"
max_entries_bar2 = 30
max_entries_bar1 = 30

barchart1 = figure.stacked_barchart(
    id=id_prefix + "bar1",
    title="Number of types",
    dataframe=dataframe,
    label_col=label_col,
    sort_col="Num. types",
    value_cols=value_cols_bar1,
    bar_names=["Class", "Abstract Class", "Interface", "Enum"],
    marker_colors=[
        "rgb(33,113,181)",
        "rgb(105,172,233)",
        "rgb(60, 160, 200)",
        "rgb(149,149,149)",
    ],
    max_entries=max_entries_bar1,
)

table = html_comp.datatable(
        id_prefix=id_prefix,
        dataframe=dataframe,
        hidden_columns=hidden_columns,
        download_name="package_complexity.csv")


barchart2 = figure.barchart(
    id=id_prefix + "bar2",
    title="Number of methods",
    dataframe=dataframe,
    value_col=value_cols_bar2,
    label_col=label_col,
    max_entries=max_entries_bar2,
)

layout = html_comp.three_row_layout(
    row1_children=html_comp.tile(
        class_name="twelve columns", id=id_prefix + "scatter-container"
    ),
    row2_children=[
        html_comp.tile(class_name="six columns", id=id_prefix + "bar1-container"),
        html_comp.tile(class_name="six columns", id=id_prefix + "bar2-container"),
    ],
    row3_children=table,
    row1_title="Package Complexity & Size",
    row2_title="Number of types and methods",
)


@app.callback(
    Output(id_prefix + "bar1-container", "children"),
    [
        Input(id_prefix + "data-table", "derived_virtual_data"),
        Input(id_prefix + "data-table", "derived_virtual_selected_rows"),
    ],
)
@cache.memoize()
def update_bar1(row_data, selected_indicies):
    if not row_data and not selected_indicies:
        raise PreventUpdate
    return controller_common.update_barchart(
        row_data,
        selected_indicies,
        barchart1,
        dataframe,
        value_cols_bar1,
        label_col,
        max_entries_bar1,
    )


@app.callback(
    Output(id_prefix + "bar2-container", "children"),
    [
        Input(id_prefix + "data-table", "derived_virtual_data"),
        Input(id_prefix + "data-table", "derived_virtual_selected_rows"),
    ],
)
@cache.memoize()
def update_bar2(row_data, selected_indicies):
    if not row_data and not selected_indicies:
        raise PreventUpdate
    return controller_common.update_barchart(
        row_data,
        selected_indicies,
        barchart2,
        dataframe,
        value_cols_bar2,
        label_col,
        max_entries_bar2,
    )


@app.callback(
    Output(id_prefix + "scatter-container", "children"),
    [
        Input(id_prefix + "data-table", "derived_virtual_data"),
        Input(id_prefix + "data-table", "derived_virtual_selected_rows"),
    ],
)
@cache.memoize()
def update_scatter(row_data, selected_indicies):
    if not row_data and not selected_indicies:
        raise PreventUpdate
    data = pd.DataFrame.from_dict(row_data) if row_data else dataframe
    return controller_common.update_scatter(
        selected_indicies,
        figure.scatter(
            id=id_prefix + "scatter",
            dataframe=data,
            label_col="Package",
            x_col="Complexity",
            y_col="Num. statements",
            size_col="Av. method complexity",
            color_col="Av. class complexity",
        ),
        data,
    )


@app.callback(
    Output(id_prefix + "download-csv", "href"),
    [Input(id_prefix + "data-table", "data")],
)
def download_csv(data):
    if data:
        controller_common.update_download_link(data)
    raise PreventUpdate


@app.callback(
    Output(id_prefix + "data-table", "hidden_columns"),
    [Input(id_prefix + "data-table-checkboxes", "value")],
)
def update_hidden_columns(selected_checkboxes):
    hidden = hidden_columns
    if selected_checkboxes:
        hidden = [col for col in hidden_columns if col not in selected_checkboxes]
    return hidden


@app.callback(
    Output(id_prefix + "data-table-paging-controll", "className"),
    [
        Input(id_prefix + "data-table-page-size", "value"),
        Input(id_prefix + "data-table", "filter_query"),
    ],
)
def update_paging_visibility(page_size, filter_query):
    page_size = 100 if not page_size else page_size
    data_size = (
        len(dataframe.index)
        if not filter_query
        else len(table_common.filter_table_data(filter_query, dataframe))
    )
    num_pages = 1 if page_size == "All" else math.ceil(data_size / int(page_size))
    if num_pages > 1:
        return "table_control"
    else:
        return "show-hide"


@app.callback(
    Output(id_prefix + "data-table", "page_current"),
    [
        Input(id_prefix + "table-prev-page", "n_clicks"),
        Input(id_prefix + "table-next-page", "n_clicks"),
        Input(id_prefix + "data-table-page-size", "value"),
        Input(id_prefix + "data-table", "filter_query"),
    ],
)
def update_page(clicks_prev, clicks_next, page_size, filter_query):
    print("update page")

    clicks_next = int(clicks_next) if clicks_next else 0
    clicks_prev = int(clicks_prev) if clicks_prev else 0
    data_size = (
        len(dataframe.index)
        if not filter_query
        else len(table_common.filter_table_data(filter_query, dataframe))
    )
    num_pages = math.ceil(
        data_size / int(data_size if page_size == "All" else page_size)
    )
    page = (clicks_next - clicks_prev) % int(num_pages)
    page = num_pages if page > num_pages else page
    return page


@app.callback(
    Output(id_prefix + "data-table-paging", "children"),
    [
        Input(id_prefix + "data-table", "page_current"),
        Input(id_prefix + "data-table", "filter_query"),
        Input(id_prefix + "data-table-page-size", "value"),
    ],
)
def update_current_page(page_current, filter_query, page_size):
    print("update current page")
    page_size = 100 if not page_size else page_size

    data_size = (
        len(dataframe.index)
        if not filter_query
        else len(table_common.filter_table_data(filter_query, dataframe))
    )
    num_pages = math.ceil(
        data_size / int(data_size if page_size == "All" else page_size)
    )
    if num_pages < 2:
        raise PreventUpdate
    return html.Label("Page %s of %s" % (page_current + 1, num_pages))


@app.callback(
    Output(id_prefix + "data-table-num-entries", "children"),
    [Input(id_prefix + "data-table", "filter_query")],
)
def update_num_entries(filter_query):
    print("update num entries")
    if not filter_query:
        return [html.Label(str(len(dataframe.index)))]
    return [
        html.Label(
            str(len(table_common.filter_table_data(filter_query, dataframe).index))
        )
    ]


@app.callback(
    Output(id_prefix + "data-table", "selected_rows"),
    [
        Input(id_prefix + "table-selected-labels", "value"),
        Input(id_prefix + "data-table", "data"),
    ],
)
def update_selected_rows(selected_label_str, table_data):
    print("update selected rows")
    if selected_label_str and len(selected_label_str.split(" ")) > 0:
        selected_labels = selected_label_str.split(" ")
        selected_rows = controller_common.get_selected_indicies(
            table_data, selected_labels
        )
        return selected_rows
    return []


@app.callback(
    Output(id_prefix + "data-table", "style_data_conditional"),
    [
        Input(id_prefix + "data-table", "selected_rows"),
        Input(id_prefix + "data-table", "data"),
    ],
)
def update_table_style(selected_rows, table_data):
    print("update table style")
    style_data = [
        {"if": {"row_index": "even"}, "backgroundColor": "#f5f6f7"},
        {"if": {"row_index": "odd"}, "backgroundColor": "#ffffff"},
    ]
    if not table_data:
        raise PreventUpdate
    if selected_rows is None:
        return style_data
    selected_indicies = []
    all_labels = pd.DataFrame.from_dict(table_data)["Package"]
    selected_labels = [all_labels[i] for i in selected_rows]
    selected_indicies = controller_common.get_selected_indicies(
        table_data, selected_labels
    )
    style_data.extend(
        [
            {"if": {"row_index": i}, "background_color": constants.SELECTED_COLOR}
            for i in selected_indicies
        ]
    )
    return style_data


def update_selected_labels_by_graph(selected_bars1, selected_bars2, selected_points):
    if selected_bars1:
        return " ".join([point.get("x") for point in selected_bars1.get("points")])
    elif selected_bars2:
        return " ".join([point.get("x") for point in selected_bars1.get("points")])
    elif selected_points:
        return " ".join(
            [point.get("hovertext") for point in selected_points.get("points")]
        )
    return ""


@app.callback(
    Output(id_prefix + "table-selected-labels", "value"),
    [
        Input(id_prefix + "data-table-deselect-all", "n_clicks_timestamp"),
        Input(id_prefix + "data-table-deselect-shown", "n_clicks_timestamp"),
        Input(id_prefix + "data-table-select-shown", "n_clicks_timestamp"),
        Input(id_prefix + "scatter", "selectedData"),
        Input(id_prefix + "bar1", "selectedData"),
        Input(id_prefix + "bar2", "selectedData"),
        Input(id_prefix + "table-prev-page", "n_clicks_timestamp"),
        Input(id_prefix + "table-next-page", "n_clicks_timestamp"),
        Input(id_prefix + "data-table", "page_size"),
        Input(id_prefix + "data-table", "filter_query"),
    ],
    state=[
        State(id_prefix + "data-table", "selected_rows"),
        State(id_prefix + "data-table", "data"),
        State(id_prefix + "table-selected-labels", "value"),
    ],
)
def update_selected_labels(
    deselect_all_tst,
    deselect_shown_tst,
    select_shown_tst,
    selected_points,
    selected_bars1,
    selected_bars2,
    _prev_clicks,
    _next_clicks,
    _page_size,
    _query,
    selected_rows,
    table_data,
    selected_labels,
):
    deselect_shown = int(deselect_shown_tst) if deselect_shown_tst else 0
    select_shown = int(select_shown_tst) if select_shown_tst else 0
    deselect_all = int(deselect_all_tst) if deselect_all_tst else 0
    if any([selected_bars1, selected_bars2, selected_points]):
        return update_selected_labels_by_graph(
            selected_bars1, selected_bars2, selected_points
        )
    elif deselect_shown > select_shown and deselect_shown > deselect_all:
        if not selected_labels:
            return ""
        labels_to_uncheck = pd.DataFrame.from_dict(table_data)[
            "Package"
        ].tolist()
        new_selected_labels = [
            selected
            for selected in selected_labels.split()
            if selected not in labels_to_uncheck
        ]
        return " ".join(set(new_selected_labels))
    elif select_shown > deselect_shown and select_shown > deselect_all:
        new_selected_labels = pd.DataFrame.from_dict(table_data)[
            "Package"
        ].tolist()
        if selected_labels and len(selected_labels.split(" ")) > 0:
            extended_selected = selected_labels.split(" ")
            extended_selected.extend(new_selected_labels)
            return " ".join(set(extended_selected))
        return " ".join(set(new_selected_labels))
    elif deselect_all > deselect_shown and deselect_all > select_shown:
        return ""
    else:
        labels_to_add = []
        if selected_rows:
            show_labels = pd.DataFrame.from_dict(table_data)[
                "Package"
            ].tolist()
            labels_to_add = [show_labels[i] for i in selected_rows]
        if selected_labels and len(selected_labels.split(" ")) > 0:
            extended_selected = selected_labels.split(" ")
            extended_selected.extend(labels_to_add)
            return " ".join(set(extended_selected))
        return " ".join(set(labels_to_add))



@app.callback(
    Output(id_prefix + "data-table", "page_size"),
    [Input(id_prefix + "data-table-page-size", "value")],
)
def update_page_size(selected_page_size):
    if not selected_page_size:
        raise PreventUpdate
    page_size = (
        int(dataframe.size) if selected_page_size == "All" else int(selected_page_size)
    )
    print("update page size to "+str(selected_page_size))
    return page_size


@app.callback(
    Output(id_prefix + "data-table", "data"),
    [
        Input(id_prefix + "data-table", "page_current"),
        Input(id_prefix + "data-table", "page_size"),
        Input(id_prefix + "data-table", "sort_by"),
        Input(id_prefix + "data-table", "filter_query"),
    ],
)
def update_table_data(page_current, page_size, sort_by, filter_query):
    print("update table data")
    page_size = len(dataframe.index) if not page_size else page_size
    page_current = 0 if not page_current else page_current
    num_ = int(page_current) * (int(page_size) + 1)
    if num_ > int(dataframe.size):
        page_current = 0
    dff = dataframe
    if filter_query:
        dff = table_common.filter_table_data(filter_query, dataframe)
    if len(sort_by):
        dff = dff.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False,
        )
    return dff.iloc[page_current * page_size : (page_current + 1) * page_size].to_dict(
        "records"
    )