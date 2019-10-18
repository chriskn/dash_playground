import dash_core_components as dcc
import dash_html_components as html
import dash_table


def tile(class_name="", id="", figure=None):
    return html.Div(
        className=class_name,
        children=dcc.Loading(id=id, children=figure, type="default"),
    )


def three_row_layout(
    row1_children,
    row2_children,
    row3_children,
    row1_title="",
    row2_title="",
    id_prefix="",
):
    return html.Div(
        className="app_main_content",
        children=[
            html.Details(
                open=True,
                className="container scalable",
                children=[
                    html.Summary(row1_title, className="summary"),
                    html.Div(id="top-row", className="row", children=row1_children),
                ],
            ),
            html.Details(
                open=True,
                className="container scalable",
                children=[
                    html.Summary(row2_title, className="summary"),
                    html.Div(id="middle-row", className="row", children=row2_children),
                ],
            ),
            html.Div(id="bottom-row", className="row", children=row3_children),
        ],
    )


def _table_controls(
    id_prefix="", download_name="data_table.csv", hidden_columns=None, num_entries=0
):
    hidden_cols = hidden_columns if hidden_columns else []
    hidden_col_options = [
        {"label": hidden_col, "value": hidden_col} for hidden_col in hidden_cols
    ]
    pagging_size_options = [
        {"label": size, "value": size} for size in ["10", "20", "50", "100", "All"]
    ]
    return [
        html.Button(
            "Select Shown",
            id=id_prefix + "data-table-select-shown",
            className="table_control_item",
        ),
        html.Button(
            "Deselect Shown",
            id=id_prefix + "data-table-deselect-shown",
            className="table_control_item",
        ),
        html.Button(
            "Deselect All",
            id=id_prefix + "data-table-deselect-all",
            className="table_control_item",
        ),
        dcc.Dropdown(
            id=id_prefix + "data-table-checkboxes",
            className="table_control_item",
            options=hidden_col_options,
            multi=True,
            placeholder="Show Hidden Columns",
        ),
        html.Div(className="table_control take_all_space"),
        html.Div(
            className="table_control table_control_item",
            children=[
                html.Label("Show ", className="table_control_item_dense"),
                dcc.Dropdown(
                    id=id_prefix + "data-table-page-size",
                    options=pagging_size_options,
                    searchable=False,
                    clearable=False,
                    multi=False,
                    placeholder="All",
                    className="table_control_item_dense",
                ),
                html.Label("of", className="table_control_item_dense"),
                html.Div(
                    id=id_prefix + "data-table-num-entries",
                    className="table_control_item_dense",
                    children=[html.Label(num_entries)],
                ),
                html.Label("entries"),
            ],
        ),
        html.A(
            html.Button("Download CSV"),
            id=id_prefix + "download-csv",
            download=download_name,
            href="",
            target="_blank",
        ),
    ]


def datatable(
    dataframe=None, id_prefix="", hidden_columns=None, download_name="table_data.csv"
):
    return html.Div(
        id=id_prefix + "table",
        className="twelve columns",
        children=[
            html.Div(
                className="table_control_outer",
                children=_table_controls(
                    id_prefix=id_prefix,
                    download_name=download_name,
                    hidden_columns=hidden_columns,
                    num_entries=len(dataframe.index),
                ),
            ),
            dcc.Input(
                type="text",
                className="show-hide",
                id=id_prefix + "table-selected-labels",
            ),
                dash_table.DataTable(
                    id=id_prefix + "data-table",
                    hidden_columns=hidden_columns,
                    columns=[{"name": i, "id": i} for i in dataframe.columns],
                    filter_action="custom",
                    row_selectable="multi",
                    page_action="none",
                    sort_action="custom",
                    sort_mode="multi",
                    sort_by=[],
                    fill_width=True,
                    data=dataframe.to_dict("records"),
                    style_header={
                        "fontWeight": "bold",
                        "backgroundColor": "#ffffff",
                        "padding": "10px 0px",
                        "textAlign": "left",
                    },
                    style_cell={"textAlign": "left"},
                    style_data_conditional=[
                        {"if": {"row_index": "even"}, "backgroundColor": "#f5f6f7"},
                        {"if": {"row_index": "odd"}, "backgroundColor": "#ffffff"},
                    ],
                ),
            html.Div(
                id=id_prefix + "data-table-paging-controll",
                className="table_control",
                children=[
                    html.Button(
                        "Previous",
                        id=id_prefix + "table-prev-page",
                        className="paging_button",
                    ),
                    html.Button(
                        "Next",
                        id=id_prefix + "table-next-page",
                        className="paging_button",
                    ),
                    html.Div(className="table_control take_all_space"),
                    html.Div(
                        id=id_prefix + "data-table-paging",
                        className="table_control_item",
                        children=[],
                    ),
                ],
            ),
        ],
    )
