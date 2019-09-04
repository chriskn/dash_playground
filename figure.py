import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px
import squarify
from colour import Color

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


def scatter(title, dataframe, label_col, x_col, y_col, size_col, color_col):
    fig = px.scatter(
        dataframe,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        hover_name=label_col,
        color_continuous_scale=px.colors.sequential.Blues,
    )
    fig.layout.title = {"text": title, "x": 0.5}
    fig.update_traces(
        marker=dict(line=dict(width=2, color="Black")), selector=dict(mode="markers")
    )
    return dcc.Graph(figure=fig)


def barchart(title, dataframe, value_col, label_col, max_entries):
    df = dataframe
    df[value_col] = df[value_col].astype("float")
    df = df.sort_values(value_col, ascending=False)
    values = list(df[value_col])[:max_entries]
    labels = list(df[label_col])[:max_entries]
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#2171b5")])
    fig.layout = go.Layout(
        title={"text": title, "x": 0.5},
        xaxis=dict(autorange=True, showgrid=False, ticks="", showticklabels=False),
    )
    return dcc.Graph(figure=fig)


def stacked_barchart():
    bar1 = go.Bar(
        x=["giraffes", "orangutans", "monkeys"], y=[20, 14, 23], name="SF Zoo"
    )
    bar2 = go.Bar(
        x=["giraffes", "orangutans", "monkeys"], y=[12, 18, 29], name="LA Zoo"
    )

    data = [bar1, bar2]
    layout = go.Layout(barmode="stack")

    return dcc.Graph(figure=go.Figure(data=data, layout=layout))


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
