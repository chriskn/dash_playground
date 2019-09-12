import pandas as pd
import urllib.parse as url_parser


def update_download_link(data):
    df = pd.DataFrame.from_dict(data)
    csv_string = df.iloc[:, ::-1].to_csv(index=False, encoding="utf-8", decimal=",")
    csv_string = "data:text/csv;charset=utf-8," + url_parser.quote(csv_string)
    return csv_string


def update_bar_data(data, fig, value_col, label_col, max_entries):
    data[value_col] = data[value_col].astype("float")
    sorted_data = data.sort_values(value_col, ascending=False)
    values = list(sorted_data[value_col])[:max_entries]
    labels = list(sorted_data[label_col])[:max_entries]
    marker_colors = ["rgb(33,113,181)"] * len(labels)
    fig.data[0].x = tuple(labels)
    fig.data[0].y = tuple(values)
    fig.data[0].marker = {"color": tuple(marker_colors)}
    return fig


def update_marker(selected_indicies, data, figure, graph_labels):
    data_labels = list(data["Package"])
    selected_labels = [data_labels[i] for i in selected_indicies]
    marker_colors = list(figure.data[0].marker.color)
    for i, label in enumerate(graph_labels):
        if label in selected_labels:
            marker_colors[i] = "rgb(255, 55, 0)"
    figure.data[0].marker.color = tuple(marker_colors)
    return figure


def update_selected_table_rows(table_data, selected_labels):
    packages_in_table = pd.DataFrame.from_dict(table_data)["Package"].tolist()
    indicies = [
        i for i, label in enumerate(packages_in_table) if label in selected_labels
    ]
    return indicies
