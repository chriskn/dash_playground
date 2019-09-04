import dash_html_components as html
import dash_core_components as dcc
import figure
import dash_table
import pandas as pd

dataframe = pd.read_csv(
    "package_complexity.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python"
)
dataframe = dataframe.drop(columns=["Path"])


def _chart(cssClassName="", chart=None):
    return html.Div(className=cssClassName, children=dcc.Loading(children=chart))


def _table(cssClassName="", data=None):
    return html.Div(
        id="table",
        className=cssClassName,
        children=dcc.Loading(
            id="tabe-loading",
            children=dash_table.DataTable(
                id="data-table",
                columns=[{"name": i, "id": i} for i in data.columns],
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                fill_width=True,
                data=data.to_dict("records"),
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
    )


content = html.Div(
    className="app_main_content",
    children=[
        html.Div(
            id="top-row",
            className="row",
            children=[
                _chart(
                    cssClassName="twelve columns",
                    chart=figure.scatter(
                        "Package Complexity & Size",
                        dataframe,
                        "Package",
                        "Complexity",
                        "Number of statements",
                        "Number of types",
                        "Number of methods",
                    ),
                )
            ],
        ),
        html.Div(
            id="middle-row",
            className="row",
            children=[
                _chart(
                    cssClassName="six columns",
                    chart=figure.barchart(
                        "Av. package complexity by class",
                        dataframe,
                        "Average complexity by class",
                        "Package",
                        50,
                    ),
                ),
                _chart(
                    cssClassName="six columns",
                    chart=dcc.Loading(
                        children=figure.barchart(
                            "Av. package complexity by method",
                            dataframe,
                            "Average complexity by method",
                            "Package",
                            50,
                        )
                    ),
                ),
            ],
        ),
        html.Div(
            id="bottom-row",
            className="row",
            children=[_table(cssClassName="twelve columns", data=dataframe)],
        ),
    ],
)
