from dash.dependencies import Input, Output, State
import pandas as pd
import figure
import html_components as html_comp
from app import app
from app import cache
from dash.exceptions import PreventUpdate
import controller_common
import time
import plotly.express as px
import constants
import dash_html_components as html
import math

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
    row3_children=html_comp.datatable(
        id_prefix=id_prefix,
        dataframe=dataframe,
        hidden_columns=hidden_columns,
        download_name="package_complexity.csv",
    ),
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
        row_data,
        selected_indicies,
        figure.scatter(
            id=id_prefix + "scatter",
            dataframe=dataframe,
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
    [Input(id_prefix + "data-table", "derived_virtual_data")],
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
    Output(id_prefix + "data-table", "page_current"),[
        Input(id_prefix+"table-prev-page", "n_clicks"),
        Input(id_prefix+"table-next-page", "n_clicks"),
        Input(id_prefix + "data-table-page-size", "value"),
        Input(id_prefix + "data-table", "filter_query"),
    ]
)
def update_page(clicks_prev, clicks_next, page_size, filter_query):
    clicks_next = int(clicks_next) if clicks_next else 0
    clicks_prev = int(clicks_prev) if clicks_prev else 0
    data_size = len(dataframe.index) if not filter_query else len(filter_table_data(filter_query))
    num_pages = math.ceil(data_size / int(data_size if page_size == "All" else page_size))
    page = (clicks_next-clicks_prev)%int(num_pages) 
    page = num_pages if page > num_pages else page
    return page


@app.callback(
    Output(id_prefix + "data-table-paging", "children"),[
        Input(id_prefix + "data-table", "page_current"),
        Input(id_prefix + "data-table", "filter_query"),
        Input(id_prefix + "data-table-page-size", "value"),
    ],
)
def update_current_page(page_current, filter_query, page_size):
    data_size = len(dataframe.index) if not filter_query else len(filter_table_data(filter_query))
    num_pages = math.ceil(data_size / int(data_size if page_size == "All" else page_size))
    return html.Label("Page %s of %s" % (page_current+1, num_pages))

@app.callback(
    Output(id_prefix+"data-table-num-entries", "children"), [
        Input(id_prefix + "data-table", "filter_query"),
    ]
)
def update_num_entries(filter_query):
    if not filter_query:
        return [
            html.Label(str(len(dataframe.index))) 
        ] 
    return [html.Label(str(len(filter_table_data(filter_query).index))) ]

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
    
    if not any(
        [
            deselect_all_tst,
            deselect_shown_tst,
            select_shown_tst,
            selected_points,
            selected_bars1,
            selected_bars2,
            table_data,
            filtered_table_data,
            selected_rows,
        ]
    ):
        raise PreventUpdate
    deselect_shown = int(deselect_shown_tst) if deselect_shown_tst else 0
    select_shown = int(select_shown_tst) if select_shown_tst else 0
    deselect_all = int(deselect_all_tst) if deselect_all_tst else 0
    if selected_bars1:
        selected_labels = [point.get("x") for point in selected_bars1.get("points")]
        return controller_common.update_selected_table_rows(table_data, selected_labels)
    elif selected_bars2:
        selected_labels = [point.get("x") for point in selected_bars2.get("points")]
        return controller_common.update_selected_table_rows(table_data, selected_labels)
    elif selected_points:
        selected_labels = [
            point.get("hovertext") for point in selected_points.get("points")
        ]
        return controller_common.update_selected_table_rows(table_data, selected_labels)
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
        return controller_common.update_selected_table_rows(
            table_data, new_selected_labels
        )
    elif select_shown > deselect_shown and select_shown > deselect_all:
        selected_labels = pd.DataFrame.from_dict(filtered_table_data)[
            "Package"
        ].tolist()
        return controller_common.update_selected_table_rows(table_data, selected_labels)
    elif deselect_all > deselect_shown and deselect_all > select_shown:
        return []
    return []


@app.callback(
    Output(id_prefix + "data-table", "style_data_conditional"),
    [
        Input(id_prefix + "data-table", "selected_rows"),
        Input(id_prefix + "data-table", "filter_query"),
        Input(id_prefix + "data-table", "data"),
    ],
    state=[
        State(id_prefix + "data-table", "derived_virtual_data"),
    ],
)
def update_table_style(selected_rows, filter, table_data, filtered_table_data):
    
    style_data = [
        {"if": {"row_index": "even"}, "backgroundColor": "#f5f6f7"},
        {"if": {"row_index": "odd"}, "backgroundColor": "#ffffff"},
    ]
    if not table_data:
        raise PreventUpdate
    if selected_rows is None:
        return style_data
    selected_indicies = []
    if filter:
        all_labels = pd.DataFrame.from_dict(table_data)["Package"]
        selected_labels = [all_labels[i] for i in selected_rows]
        filtered_labels = pd.DataFrame.from_dict(filtered_table_data)["Package"]
        selected_indicies = [
            i for i, label in enumerate(filtered_labels) if label in selected_labels
        ]
    elif not filter:
        all_labels = dataframe["Package"]
        selected_labels = [all_labels[i] for i in selected_rows]
        selected_indicies = [
            i for i, label in enumerate(all_labels) if label in selected_labels
        ]
    style_data.extend(
        [
            {"if": {"row_index": i}, "background_color": constants.SELECTED_COLOR}
            for i in selected_indicies
        ]
    )
    return style_data



@app.callback(
    Output(id_prefix + "data-table", "page_size"),
    [
        Input(id_prefix + "data-table-page-size", "value"),
    ]
)
def update_page_size(selected_page_size):
    page_size = int(dataframe.size) if selected_page_size=="All" else int(selected_page_size)
    return page_size

@app.callback(
    Output(id_prefix + "data-table", "data"),
    [Input(id_prefix + "data-table", "page_current"),
     Input(id_prefix + "data-table", "page_size"),
     Input(id_prefix + "data-table", "sort_by"),
     Input(id_prefix + "data-table", "filter_query")]
)
def update_table_data(page_current, page_size, sort_by, filter_query):
    
    
    
    num_ = int(page_current)*(int(page_size)+1)
    
    if num_ > int(dataframe.size):
        
        page_current = 0         
    dff = dataframe
    if filter_query:
        dff = filter_table_data(filter_query)
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )
    return dff.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

def filter_table_data(filter):
    filtering_expressions = filter.split(' && ')
    dff = dataframe
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    return dff