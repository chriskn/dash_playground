import dash_html_components as html
import dash_core_components as dcc
import figure
import dash_table


def content(dataframe):
    num_data = 30
    dataframe.sort_values("Average complexity by class", ascending=False)
    av_comp_by_cls = list(
            filter(
                lambda x: x > 0, map(float, dataframe["Average complexity by class"])
            ),
    )[:num_data]
    av_comp_by_cls_labels = dataframe["Package"][:num_data]

    dataframe.sort_values("Average complexity by method", ascending=False)
    av_comp_by_meth = list(
            filter(
                lambda x: x > 0, map(float, dataframe["Average complexity by method"])
            )        
    )[:num_data]
    av_comp_by_meth_labels = dataframe["Package"][:num_data]

    dataframe.sort_values("Complexity", ascending=False)
    comp = sorted(
        list(filter(lambda x: x > 0, map(int, dataframe["Complexity"]))), reverse=True
    )[:num_data]
    comp_labels = dataframe["Package"][:num_data]

    dataframe.sort_values("Number of statements", ascending=False)
    num_statements = sorted(
        list(filter(lambda x: x > 0, map(int, dataframe["Number of statements"]))),
        reverse=True,
    )[:num_data]
    num_statements_labels = dataframe["Package"][:num_data]


    return html.Div(
        className="app_main_content",
        children=[
            html.Div(
                id="top-row",
                className="row",
                children=[
                    _chart(
                        cssClassName="six columns",
                        chart=figure.barchart(
                            "Number of statements by package",
                            num_statements,
                            num_statements_labels,
                        ),
                    ),
                    _chart(
                        cssClassName="six columns",
                        #chart=figure.treemap("Package complexity", comp, comp_labels),
                        chart = figure.scatter(dataframe, "Package", "Complexity", "Number of statements", "Number of types", "Number of methods")
                    ),
                ],
            ),
            html.Div(
                id="middle-row",
                className="row",
                children=[
                    _chart(
                        cssClassName="six columns",
                        chart=figure.treemap(
                            "Av. package complexity by class",
                            av_comp_by_cls,
                            av_comp_by_cls_labels,
                        ),
                    ),
                    _chart(
                        cssClassName="six columns",
                        chart=dcc.Loading(
                            children=figure.treemap(
                                "Av. package complexity by method",
                                av_comp_by_meth,
                                av_comp_by_meth_labels,
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
                # style_as_list_view=True,
                style_header={
                    "textTransform": "Uppercase",
                    "fontWeight": "bold",
                    "backgroundColor": "#ffffff",
                    "padding": "10px 0px",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "even"},
                        "backgroundColor": "#f5f6f7",
                        "textAlign": "left",
                    },
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#ffffff",
                        "textAlign": "left",
                    },
                ],
            ),
        ),
    )
