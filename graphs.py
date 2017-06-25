import seaborn
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
import bokeh.palettes
from bokeh.models import CustomJS, Slider, ColumnDataSource, Palette, Select, ColorMapper
import pandas as pd
from matplotlib import pyplot


def palette_maps(n_colors):


    palette_map = {}

    for n in pyplot.colormaps():

        if n == "jet":

            continue

        palette_map.update({n: seaborn.color_palette(n, n_colors).as_hex()})

    return palette_map


def plot_scatter(x, y, **kwargs):

    if isinstance(y, pd.Series) and isinstance(x, pd.DataFrame):
        num_xs = len(x.columns)
        palettes = palette_maps(num_xs)
        palette = palettes[kwargs["palette"]]

        ys = y.repeat(num_xs).values
        xs = x.values.flatten()
        colors = palette * (len(xs)/len(palette))

    elif isinstance(y, pd.DataFrame) and isinstance(x, pd.DataFrame):

        num_xs = len(x.columns)
        palettes = palette_maps(num_xs)
        palette = palettes[kwargs["palette"]]

        if num_xs != len(y.columns):

            raise ValueError("If y values are dataframe, number of y columns needs to equal number of x columns. "
                             "If y is the same value repeated for each x then pass y as a series")

        ys = y.values.flatten()
        xs = x.values.flatten()
        colors = palette * (len(xs)/len(palette))

    elif isinstance(y, pd.DataFrame) and isinstance(x, pd.Series):

        num_ys = len(y.columns)
        palettes = palette_maps(num_ys)
        palette = palettes[kwargs["palette"]]

        xs = x.repeat(num_ys).values
        ys = y.values.flatten()

        colors = palette * (len(ys)/len(palette))

    elif isinstance(y, pd.Series) and isinstance(x, pd.Series):

        palettes = palette_maps(1)
        palette = palettes[kwargs["palette"]]

        xs = x.tolist()
        ys = y.tolist()
        colors = palette * len(ys)

    else:

        raise ValueError

    p = figure(plot_width=kwargs["plot_width"], plot_height=kwargs["plot_height"])
    source = ColumnDataSource(data=dict(x=xs, y=ys, color=colors))
    col_source = ColumnDataSource(data=palettes)
    sc = p.scatter('x', 'y', color="color", source=source)

    def callback(source=source, sc=sc, window=None):

        f = cb_obj.value
        sc.glyph.size = f
        source.change.emit()

    def callback_pal(source=source, col=col_source, window=None):

        data = source.data
        new_pal = col.data[cb_obj.value]

        pal_map = {}
        pal = []
        for d in data["color"]:

            if d not in pal:

                pal.append(d)

        for c in range(len(pal)):

            pal_map[pal[c]] = new_pal[c]

        for i in range(len(data["color"])):

            new_col = pal_map[data["color"][i]]
            data["color"][i] = new_col

        source.change.emit()

    # [u'#7fc97f', u'#bdaed3']

    # pal = []
    # for d in data["color"]:
    #
    #     if d not in pal:
    #         pal.append(d)
    #
    # pal_map = dict()
    #
    # for c in pal:
    #     pal_map.update({c: "#3a5254"})
    # new_pal[pal.index(p)]

    dot_size_slider = Slider(start=0, end=100, value=1, step=1, title="Dot Size",
                             callback=CustomJS.from_py_func(callback))
    select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"],
                        callback=CustomJS.from_py_func(callback_pal))
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components({"p": p, "dot_size_slider": dot_size_slider, "pal": select_pal}, INLINE)

    return script, div, js_resources, css_resources

if __name__ == '__main__':

    df = pd.DataFrame(np.random.randn(10, 4), columns=["x1", "x2", "y1", "y2"])

    plot_scatter(df[["x1", "x2"]], df[["y1", "y2"]], palette="Accent", plot_width=600, plot_height=600)
