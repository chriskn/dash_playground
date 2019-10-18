import dash_core_components as dcc
import plotly.graph_objs as go
import squarify
from colour import Color
import plotly.express as px
from plotly.graph_objs.layout import Legend

BASE_COLOR = Color(rgb=(0.26, 0.57, 0.78))


def to_plotly_rgb(color):
    return (
        "rgb("
        + str(color.rgb[0] * 255)
        + ","
        + str(color.rgb[1] * 255)
        + ","
        + str(color.rgb[2] * 255)
        + ")"
    )


def treemap(title, values, labels):
    fig = go.Figure()
    x = 0.0
    y = 0.0
    width = 100.0
    height = 100.0
    normed = squarify.normalize_sizes(values, width, height)
    rects = squarify.squarify(normed, x, y, width, height)
    colors = [
        to_plotly_rgb(c)
        for c in list(BASE_COLOR.range_to(Color("Yellow"), len(values)))
    ]
    shapes = []
    annotations = []
    counter = 0
    for r, val, label, color in zip(rects, values, labels, colors):
        shapes.append(
            dict(
                type="rect",
                x0=r["x"],
                y0=r["y"],
                x1=r["x"] + r["dx"],
                y1=r["y"] + r["dy"],
                line=dict(width=2),
                fillcolor=color,
            )
        )
        annotations.append(
            dict(
                x=r["x"] + (r["dx"] / 2),
                y=r["y"] + (r["dy"] / 2),
                text=val,
                showarrow=False,
            )
        )
    # For hover text
    fig.add_trace(
        go.Scatter(
            x=[r["x"] + (r["dx"] / 2) for r in rects],
            y=[r["y"] + (r["dy"] / 2) for r in rects],
            text=[label for label in labels],
            mode="text",
        )
    )
    fig.layout = go.Layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        shapes=shapes,
        annotations=annotations,
        hovermode="closest",
        title=title,
    )
    return dcc.Graph(figure=fig)





def scatter(
    id="",
    dataframe=None,
    label_col=None,
    x_col=None,
    y_col=None,
    size_col=None,
    color_col=None,
    size_min=None,
):
    fig = px.scatter(
        dataframe,
        x=x_col,
        y=y_col,
        size=size_col,
        hover_name=label_col,
        color=color_col,
        color_continuous_scale=px.colors.sequential.Blues,
        height=400,
        render_mode='webgl'
    )
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color="Black"),
            sizemin=size_min if size_min else 4,
            reversescale=True,
        ),
        selector=dict(mode="markers"),
    )
    fig.layout.clickmode = "event+select"
    if not color_col:
        fig.data[0].marker.color = "rgba(33,113,181, 0.9)"
    return dcc.Graph(figure=fig, id=id)


def barchart(
    id="", title="", dataframe=None, value_col="", label_col="", max_entries=0
):
    dataframe[value_col] = dataframe[value_col].astype("float")
    values = list(dataframe[value_col])[:max_entries]
    labels = list(dataframe[label_col])[:max_entries]
    marker_colors = ["rgb(33,113,181)"] * len(labels)
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=marker_colors)])
    fig.layout = go.Layout(
        title={"text": title, "x": 0.5},
        xaxis=dict(autorange=True, showgrid=False, ticks="", showticklabels=False),
        clickmode="event+select",
        height=400,
    )
    return dcc.Graph(figure=fig, id=id)


def stacked_barchart(
    id="",
    title=None,
    label_col="",
    sort_col="",
    dataframe=None,
    value_cols=None,
    bar_names=None,
    marker_colors=None,
    max_entries=0,
):
    labels = dataframe[label_col][:max_entries]
    bars = []
    for i, value_col in enumerate(value_cols):
        name = bar_names[i] if bar_names else value_col
        bar = go.Bar(
            x=labels,
            y=dataframe[value_col][:max_entries],
            name=name,
            marker_color=marker_colors[i],
        )
        bars.append(bar)
    data = bars
    legend = Legend(font=dict(size=12))
    layout = go.Layout(
        legend=legend,
        legend_orientation="h",
        barmode="stack",
        xaxis=dict(autorange=True, showgrid=False, ticks="", showticklabels=False),
        clickmode="event+select",
        height=400,
    )
    if title:
        layout.title = {"text": title, "x": 0.5}
    return dcc.Graph(id=id, figure=go.Figure(data=data, layout=layout))


def heatmap(title):
    return dcc.Graph(
        figure={
            "data": [
                go.Heatmap(
                    x=["1x", "2x", "3x"],
                    y=["1y", "2y", "3y"],
                    z=["2000", "2001", "2002"],
                    colorscale="Reds",
                    colorbar={"title": "Percentage"},
                    showscale=True,
                )
            ],
            "layout": {"title": title},
        }
    )
