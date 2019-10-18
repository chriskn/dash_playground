from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import figure
import html_components as html_comp
import controller.table as table_controller
import controller.chart as chart_controller
from app import app
from app import cache
import dash_html_components as html
from utils import timing

DATAFRAME = pd.read_csv(
    "package_complexity.csv",
    sep=";",
    decimal=",",
    header=0,
    encoding="ascii",
    engine="python",
)


ID_PREFIX = "pcomp"
DATAFRAME.columns = [
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
HIDDEN_COLUMNS = [
    "Num. classes",
    "Num. abstract classes",
    "Num. interfaces",
    "Num. enums",
    "Project",
    "Path",
]
VALUE_COLS_BAR2 = ["Num. methods"]
VALUE_COLS_BAR1 = [
    "Num. classes",
    "Num. abstract classes",
    "Num. interfaces",
    "Num. enums",
]
LABEL_COL = "Package"
MAX_ENTRIES_BARCHART = 30

TYPES_BARCHART = figure.stacked_barchart(
    id=ID_PREFIX + "bar1",
    title="Number of types",
    dataframe=DATAFRAME,
    label_col=LABEL_COL,
    sort_col="Num. types",
    value_cols=VALUE_COLS_BAR1,
    bar_names=["Class", "Abstract Class", "Interface", "Enum"],
    marker_colors=[
        "rgb(33,113,181)",
        "rgb(105,172,233)",
        "rgb(60, 160, 200)",
        "rgb(149,149,149)",
    ],
    max_entries=MAX_ENTRIES_BARCHART,
)

HTML_TABLE = html_comp.datatable(
    id_prefix=ID_PREFIX,
    dataframe=DATAFRAME,
    hidden_columns=HIDDEN_COLUMNS,
    download_name="package_complexity.csv",
)


METHODS_BARCHART = figure.barchart(
    id=ID_PREFIX + "bar2",
    title="Number of methods",
    dataframe=DATAFRAME,
    value_col=VALUE_COLS_BAR2,
    label_col=LABEL_COL,
    max_entries=MAX_ENTRIES_BARCHART,
)

LAYOUT = html_comp.three_row_layout(
    row1_children=html_comp.tile(
        class_name="twelve columns", id=ID_PREFIX + "scatter-container"
    ),
    row2_children=[
        html_comp.tile(class_name="six columns", id=ID_PREFIX + "bar1-container"),
        html_comp.tile(class_name="six columns", id=ID_PREFIX + "bar2-container"),
    ],
    row3_children=HTML_TABLE,
    row1_title="Package Complexity & Size",
    row2_title="Number of types and methods",
)


@app.callback(
    Output(ID_PREFIX + "bar1-container", "children"),
    [
        Input(ID_PREFIX + "data-table", "derived_virtual_data"),
        Input(ID_PREFIX + "data-table", "derived_virtual_selected_rows"),
    ],
)
@timing
@cache.memoize()
def update_bar1(row_data, selected_indices):
    if not row_data and not selected_indices:
        raise PreventUpdate
    return chart_controller.update_barchart(
        row_data,
        selected_indices,
        TYPES_BARCHART,
        DATAFRAME,
        VALUE_COLS_BAR1,
        LABEL_COL,
        MAX_ENTRIES_BARCHART,
    )


@app.callback(
    Output(ID_PREFIX + "bar2-container", "children"),
    [
        Input(ID_PREFIX + "data-table", "derived_virtual_data"),
        Input(ID_PREFIX + "data-table", "derived_virtual_selected_rows"),
    ],
)
@timing
@cache.memoize()
def update_bar2(row_data, selected_indices):
    if not row_data and not selected_indices:
        raise PreventUpdate
    return chart_controller.update_barchart(
        row_data,
        selected_indices,
        METHODS_BARCHART,
        DATAFRAME,
        VALUE_COLS_BAR2,
        LABEL_COL,
        MAX_ENTRIES_BARCHART,
    )


@app.callback(
    Output(ID_PREFIX + "scatter-container", "children"),
    [
        Input(ID_PREFIX + "data-table", "derived_virtual_data"),
        Input(ID_PREFIX + "data-table", "derived_virtual_selected_rows"),
    ],
)
@timing
@cache.memoize()
def update_scatter(row_data, selected_indices):
    if not row_data and not selected_indices:
        raise PreventUpdate
    data = pd.DataFrame.from_dict(row_data) if row_data else DATAFRAME
    return chart_controller.update_scatter(
        selected_indices,
        figure.scatter(
            id=ID_PREFIX + "scatter",
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
    Output(ID_PREFIX + "download-csv", "href"),
    [Input(ID_PREFIX + "data-table", "data")],
)
@timing
@cache.memoize()
def download_csv(data):
    if data:
        return table_controller.update_download_link(data)
    raise PreventUpdate


@app.callback(
    Output(ID_PREFIX + "data-table", "hidden_columns"),
    [Input(ID_PREFIX + "data-table-checkboxes", "value")],
)
@timing
@cache.memoize()
def update_hidden_columns(selected_checkboxes):
    return table_controller.update_hidden_columns(selected_checkboxes, HIDDEN_COLUMNS)


@app.callback(
    Output(ID_PREFIX + "data-table-paging-controll", "className"),
    [
        Input(ID_PREFIX + "data-table-page-size", "value"),
        Input(ID_PREFIX + "data-table", "filter_query"),
    ],
)
@timing
@cache.memoize()
def update_paging_visibility(page_size, filter_query):
    return table_controller.update_paging_visibility(page_size, filter_query, DATAFRAME)


@app.callback(
    Output(ID_PREFIX + "data-table", "page_current"),
    [
        Input(ID_PREFIX + "table-prev-page", "n_clicks"),
        Input(ID_PREFIX + "table-next-page", "n_clicks"),
        Input(ID_PREFIX + "data-table-page-size", "value"),
        Input(ID_PREFIX + "data-table", "filter_query"),
    ],
)
@timing
@cache.memoize()
def update_page(clicks_prev, clicks_next, page_size, filter_query):
    return table_controller.update_page(
        clicks_prev, clicks_next, page_size, filter_query, DATAFRAME
    )


@app.callback(
    Output(ID_PREFIX + "data-table-paging", "children"),
    [
        Input(ID_PREFIX + "data-table", "page_current"),
        Input(ID_PREFIX + "data-table", "filter_query"),
        Input(ID_PREFIX + "data-table-page-size", "value"),
    ],
)
@timing
@cache.memoize()
def update_current_page(page_current, filter_query, page_size):
    num_pages = table_controller.calc_num_pages(filter_query, page_size, DATAFRAME)
    if num_pages < 2:
        raise PreventUpdate
    return html.Label("Page %s of %s" % (page_current + 1, num_pages))


@app.callback(
    Output(ID_PREFIX + "data-table-num-entries", "children"),
    [Input(ID_PREFIX + "data-table", "filter_query")],
)
@timing
@cache.memoize()
def update_num_entries(filter_query):
    return [html.Label(str(table_controller.calc_num_entries(filter_query, DATAFRAME)))]


@app.callback(
    Output(ID_PREFIX + "data-table", "selected_rows"),
    [
        Input(ID_PREFIX + "table-selected-labels", "value"),
        Input(ID_PREFIX + "data-table", "data"),
    ],
)
@timing
@cache.memoize()
def update_selected_rows(selected_label_str, table_data):
    return table_controller.update_selected_rows(
        selected_label_str, table_data, "Package"
    )


@app.callback(
    Output(ID_PREFIX + "data-table", "style_data_conditional"),
    [
        Input(ID_PREFIX + "data-table", "selected_rows"),
        Input(ID_PREFIX + "data-table", "data"),
    ],
)
@timing
@cache.memoize()
def update_table_style(selected_rows, table_data):
    if not table_data:
        raise PreventUpdate
    return table_controller.update_table_style(selected_rows, table_data, "Package")

@app.callback(
    Output(ID_PREFIX + "table-selected-labels", "value"),
    [
        Input(ID_PREFIX + "data-table-deselect-all", "n_clicks_timestamp"),
        Input(ID_PREFIX + "data-table-deselect-shown", "n_clicks_timestamp"),
        Input(ID_PREFIX + "data-table-select-shown", "n_clicks_timestamp"),
        Input(ID_PREFIX + "scatter", "selectedData"),
        Input(ID_PREFIX + "bar1", "selectedData"),
        Input(ID_PREFIX + "bar2", "selectedData"),
        Input(ID_PREFIX + "table-prev-page", "n_clicks_timestamp"),
        Input(ID_PREFIX + "table-next-page", "n_clicks_timestamp"),
        Input(ID_PREFIX + "data-table", "page_size"),
        Input(ID_PREFIX + "data-table", "filter_query"),
    ],
    state=[
        State(ID_PREFIX + "data-table", "selected_rows"),
        State(ID_PREFIX + "data-table", "data"),
        State(ID_PREFIX + "table-selected-labels", "value"),
    ],
)
@timing
@cache.memoize()
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
    return table_controller.update_selected_labels(
        deselect_all_tst,
        deselect_shown_tst,
        select_shown_tst,
        selected_points,
        selected_bars1,
        selected_bars2,
        selected_rows,
        table_data,
        selected_labels,
    )


@app.callback(
    Output(ID_PREFIX + "data-table", "page_size"),
    [Input(ID_PREFIX + "data-table-page-size", "value")],
)
@timing
@cache.memoize()
def update_page_size(selected_page_size):
    if not selected_page_size:
        raise PreventUpdate
    return table_controller.calc_page_size(selected_page_size, DATAFRAME)


@app.callback(
    Output(ID_PREFIX + "data-table", "data"),
    [
        Input(ID_PREFIX + "data-table", "page_current"),
        Input(ID_PREFIX + "data-table", "page_size"),
        Input(ID_PREFIX + "data-table", "sort_by"),
        Input(ID_PREFIX + "data-table", "filter_query"),
    ],
)
@timing
@cache.memoize()
def update_table_data(page_current, page_size, sort_by, filter_query):
    return table_controller.update_table_data(
        page_current, page_size, sort_by, filter_query, DATAFRAME
    )
