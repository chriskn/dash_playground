import dash_core_components as dcc
import dash_html_components as html
import dash_table


def tile(class_name="", id="", figure=None):
    return html.Div(className=class_name, children=dcc.Loading(id=id, children=figure))


def three_row_layout(row1_children, row2_children, row3_children, id_prefix=""):
    return html.Div(
        className="app_main_content",
        children=[
            html.Details(
                open=True,
                className="container scalable",
                children=[
                    html.Summary("Package Complexity & Size", className="summary"),
                    html.Div(id="top-row", className="row", children=row1_children),
                ],
            ),
            html.Details(
                open=True,
                className="container scalable",
                children=[
                    html.Summary("Number of Methods & Classes", className="summary"),
                    html.Div(id="middle-row", className="row", children=row2_children),
                ],
            ),
            html.Div(id="bottom-row", className="row", children=row3_children),
        ],
    )


def datatable(
    dataframe=None, id_prefix="", hidden_columns=None, download_name="table_data.csv"
):
    return html.Div(
        id=id_prefix + "table",
        className="twelve columns",
        children=[
            html.Div(
                children=[
                    html.Div(
                        className="table_control",
                        children=[
                            html.A(
                                "Deselect All",
                                id=id_prefix + "data-table-deselect-all",
                                className="table_control_item",
                            ),
                            html.A(
                                "Deselect Shown",
                                id=id_prefix + "data-table-deselect-shown",
                                className="table_control_item",
                            ),
                            html.A(
                                "Select Shown",
                                id=id_prefix + "data-table-select-shown",
                                className="table_control_item",
                            ),
                            html.A(
                                "Download CSV",
                                className="table_control_item",
                                id=id_prefix + "download-csv",
                                download=download_name,
                                href="",
                                target="_blank",
                            ),
                            dcc.Checklist( 
                                id=id_prefix + "data-table-checkboxes",
                                className="table_control",
                                labelClassName="table_control_item",
                                options=[
                                    {"label": "Show Paths", "value": "showPaths"},
                                    {"label": "Show Projects", "value": "showProjects"},
                                ], 
                            ),
                        ],
                    )
                ]
            ),
            dcc.Loading(
                id=id_prefix + "tabe-loading",
                children=dash_table.DataTable(
                    id=id_prefix + "data-table",
                    hidden_columns=hidden_columns,
                    columns=[{"name": i, "id": i} for i in dataframe.columns],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_selectable="multi",
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
        ],
    )
