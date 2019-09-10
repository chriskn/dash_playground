import dash_core_components as dcc
import dash_html_components as html
import dash_table


def datatable(
    dataframe=None, id_prefix="", hidden_columns=None, download_name="table_data.csv"
):
    return html.Div(
        id=id_prefix + "table",
        className="twelve columns",
        children=[
            html.A(
                "Download CSV",
                className="download-link",
                id=id_prefix + "download-csv",
                download=download_name,
                href="",
                target="_blank",
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
