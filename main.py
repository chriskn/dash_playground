from dash.dependencies import Input, Output
import dash
import dash_table
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import flask
import figure
import dash_bootstrap_components as dbc

app = dash.Dash("Sat")
#app.config.suppress_callback_exceptions = True
app.title = "Sat"

dataframe = pd.read_csv(
    "package_complexity.csv", sep="\s*;\s*", header=0, encoding="ascii", engine="python"
)
dataframe = dataframe.drop(columns=["Path"])

table = html.Div(
    id="table",
    className="twelve columns",
    children=dcc.Loading(
        id="tabe-loading",
        children=dash_table.DataTable(
            id="data-table",
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
)


def _chart(cssClassName="", id="", chart=None):
    return html.Div(className=cssClassName, id=id, children=dcc.Loading(children=chart))


def scatter_plot(data):
    return _chart(
        cssClassName="twelve columns",
        chart=figure.scatter(
            id="scatter",
            dataframe=data,
            label_col="Package",
            x_col="Complexity",
            y_col="Number of statements",
            size_col="Average class complexity",
            color_col="Average method complexity",
        ),
    )


def barchart1(data, selected=None):
    return _chart(
        cssClassName="six columns",
        id="bar1-container",
        chart=figure.barchart(
            id="bar1",
            title="Number of classes interfaces and enums in package",
            dataframe=data,
            value_col="Number of types",
            label_col="Package",
            max_entries=50,
            marked_labels = selected
        ),
    )


def barchart2(data, selected=None):
    return _chart(
        cssClassName="six columns",
        id="bar2-container",
        chart=figure.barchart(
            id="bar2",
            title="Number of methods in package",
            dataframe=data,
            value_col="Number of methods",
            label_col="Package",
            max_entries=50,
            marked_labels = selected
        ),
    )


main_content = html.Div(
    className="app_main_content",
    children=[
        html.Details(
            open=True,
            className="container scalable",
            children=[
                html.Summary(id="title" "Package Complexity & Size", className="summary"),
                html.Div(
                    id="top-row", className="row", children=scatter_plot(dataframe)
                ),
            ],
        ),
        html.Details(
            open=True,
            className="container scalable",
            children=[
                html.Summary("Number of Methods & Classes", className="summary"),
                html.Div(
                    id="middle-row",
                    className="row",
                    children=[barchart1(dataframe), barchart2(dataframe)],
                ),
            ],
        ),
        html.Div(id="bottom-row", className="row", children=table),
    ],
)


app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(src=app.get_asset_url("plotly_logo.png")),
                html.H6("SAT"),
            ],
        ),
        html.Div(
            className="twelve columns",
            children=html.Div(
                [
                    html.H5(
                        "Package complexity & size reports from 30.08.2019 14:21:14"
                    ),
                    main_content,
                ]
            ),
        ),
    ],
)


@app.callback(
    Output("top-row", "children"), [Input("data-table", "derived_virtual_data")]
)
def update_top(data):
    data = pd.DataFrame.from_dict(data) if data else dataframe
    return scatter_plot(data)


@app.callback(
    Output("middle-row", "children"), [
    Input("data-table", "derived_virtual_data"),   
    Input('data-table', 'derived_virtual_selected_rows') 
    ]
)
def update_middle(filter_data, selected_indicies):
    data = pd.DataFrame.from_dict(filter_data) if filter_data else dataframe
    selected_labels = []
    if selected_indicies:
        labels = data["Package"]    
        selected_labels  = [labels[i] for i in selected_indicies]  
    return [barchart1(data, selected_labels), barchart2(data, selected_labels)]


# @app.callback(
#     Output("bar2", "figure"), [Input("scatter", "selectedData"), Input("bar1", "clickData")], state = [State('bar2', 'figure')]
# )
# def on_scatter_click(data_scatter, data_bar1, bar2):
#     if data_scatter:
#         print("scatter klicked on "+str(data_scatter))
#     if data_bar1:
#         print("bar1 klicked on "+str(data_bar1))
#         print("bar2 "+str(bar2))
#         #return {'points': [{'pointNumber': 1, 'pointIndex': 1}]}


if __name__ == "__main__":
    app.run_server(debug=True)
