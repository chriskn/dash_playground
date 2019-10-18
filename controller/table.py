import pandas as pd
import urllib.parse as url_parser
import io
import math
import constants

_OPERATORS = [
    ["ge ", ">="],
    ["le ", "<="],
    ["lt ", "<"],
    ["gt ", ">"],
    ["ne ", "!="],
    ["eq ", "="],
    ["contains "],
    ["datestartswith "],
]


def _split_filter_part(filter_part):
    for operator_type in _OPERATORS:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1 : name_part.rfind("}")]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', "`"):
                    value = value_part[1:-1].replace("\\" + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def calc_num_pages(filter_query, page_size, dataframe):
    num_data = len(dataframe.index)
    page_size = num_data if not page_size else page_size
    data_size = (
        num_data
        if not filter_query
        else len(filter_table_data(filter_query, dataframe))
    )
    num_pages = math.ceil(
        data_size / int(data_size if page_size == "All" else page_size)
    )
    return num_pages


def calc_num_entries(filter_query, dataframe):
    if not filter_query:
        return len(dataframe.index)
    return len(filter_table_data(filter_query, dataframe).index)


def calc_page_size(selected_page_size, dataframe):
    return (
        len(dataframe.index) if selected_page_size == "All" else int(selected_page_size)
    )


def update_selected_rows(selected_label_str, table_data, label_column):
    if selected_label_str and len(selected_label_str.split(" ")) > 0:
        selected_labels = selected_label_str.split(" ")
        selected_rows = get_selected_indices(table_data, selected_labels, label_column)
        return selected_rows
    return []


def update_page(clicks_prev_ts, clicks_next_ts, page_size, filter_query, dataframe):
    clicks_next_ts = int(clicks_next_ts) if clicks_next_ts else 0
    clicks_prev_ts = int(clicks_prev_ts) if clicks_prev_ts else 0
    data_size = (
        len(dataframe.index)
        if not filter_query
        else len(filter_table_data(filter_query, dataframe))
    )

    num_pages = (
        1
        if not page_size or page_size == "All"
        else math.ceil(data_size / int(page_size))
    )
    page = (clicks_next_ts - clicks_prev_ts) % int(num_pages)
    page = num_pages if page > num_pages else page
    return page


def update_hidden_columns(selected_hidden_cols, all_hidden_cols):
    hidden = all_hidden_cols
    if selected_hidden_cols:
        hidden = [col for col in all_hidden_cols if col not in selected_hidden_cols]
    return hidden


def update_paging_visibility(page_size, filter_query, dataframe):
    num_all = len(dataframe.index)
    page_size = num_all if not page_size else page_size
    data_size = (
        num_all if not filter_query else len(filter_table_data(filter_query, dataframe))
    )
    num_pages = 1 if page_size == "All" else math.ceil(data_size / int(page_size))
    if num_pages > 1:
        return "table_control"
    else:
        return "show-hide"


def update_download_link(data):
    dataframe = pd.DataFrame.from_dict(data)
    output = io.StringIO()
    output.write("data:text/csv;charset=utf-8,")
    output.write(
        url_parser.quote(
            dataframe.iloc[:, ::-1].to_csv(
                index=False, encoding="utf-8", decimal=",", sep=";"
            )
        )
    )
    output.seek(0)
    return output.getvalue()


def get_selected_indices(table_data, selected_labels, label_column):
    packages_in_table = pd.DataFrame.from_dict(table_data)[label_column].tolist()
    indices = [
        i for i, label in enumerate(packages_in_table) if label in selected_labels
    ]
    return indices


def update_table_style(selected_rows, table_data, label_column):
    style_data = [
        {"if": {"row_index": "even"}, "backgroundColor": "#f5f6f7"},
        {"if": {"row_index": "odd"}, "backgroundColor": "#ffffff"},
    ]
    if selected_rows is None:
        return style_data
    selected_indices = []
    all_labels = pd.DataFrame.from_dict(table_data)[label_column]
    selected_labels = [all_labels[i] for i in selected_rows]
    selected_indices = get_selected_indices(table_data, selected_labels, label_column)
    style_data.extend(
        [
            {"if": {"row_index": i}, "background_color": constants.SELECTED_COLOR}
            for i in selected_indices
        ]
    )
    return style_data


def filter_table_data(filter_query, dataframe):
    filtering_expressions = filter_query.split(" && ")
    dff = dataframe
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = _split_filter_part(filter_part)

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == "contains":
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    return dff


def update_table_data(page_current, page_size, sort_by, filter_query, dataframe):
    data_size = len(dataframe.index)
    page_size = data_size if not page_size else page_size
    page_current = 0 if not page_current else page_current
    num_entries_per_page = int(page_current) * (int(page_size) + 1)
    if num_entries_per_page > data_size:
        page_current = 0
    dataframe_copy = dataframe
    if filter_query:
        dataframe_copy = filter_table_data(filter_query, dataframe)
    if len(sort_by) > 0:
        dataframe_copy = dataframe_copy.sort_values(
            [col["column_id"] for col in sort_by],
            ascending=[col["direction"] == "asc" for col in sort_by],
            inplace=False,
        )
    return dataframe_copy.iloc[
        page_current * page_size : (page_current + 1) * page_size
    ].to_dict("records")


def update_selected_labels_by_graph(selected_bars1, selected_bars2, selected_points):
    if selected_bars1:
        return " ".join([point.get("x") for point in selected_bars1.get("points")])
    elif selected_bars2:
        return " ".join([point.get("x") for point in selected_bars2.get("points")])
    elif selected_points:
        return " ".join(
            [point.get("hovertext") for point in selected_points.get("points")]
        )
    return ""


def update_selected_labels(
    deselect_all_tst,
    deselect_shown_tst,
    select_shown_tst,
    selected_points,
    selected_bars1,
    selected_bars2,
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
        labels_to_uncheck = pd.DataFrame.from_dict(table_data)["Package"].tolist()
        new_selected_labels = [
            selected
            for selected in selected_labels.split()
            if selected not in labels_to_uncheck
        ]
        return " ".join(set(new_selected_labels))
    elif select_shown > deselect_shown and select_shown > deselect_all:
        new_selected_labels = pd.DataFrame.from_dict(table_data)["Package"].tolist()
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
            show_labels = pd.DataFrame.from_dict(table_data)["Package"].tolist()
            labels_to_add = [show_labels[i] for i in selected_rows]
        if selected_labels and len(selected_labels.split(" ")) > 0:
            extended_selected = selected_labels.split(" ")
            extended_selected.extend(labels_to_add)
            return " ".join(set(extended_selected))
        return " ".join(set(labels_to_add))
