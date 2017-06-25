import seaborn
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models import CustomJS, Slider, ColumnDataSource, Select
import pandas as pd


def plot_scatter(x, y, **kwargs):

    if isinstance(y, pd.Series) and isinstance(x, pd.DataFrame):
        num_xs = len(x.columns)
        palette = seaborn.color_palette(kwargs["palette"], num_xs).as_hex()

        ys = y.repeat(num_xs).values
        xs = x.values.flatten()
        colors = palette * (len(xs)/len(palette))

    elif isinstance(y, pd.DataFrame) and isinstance(x, pd.DataFrame):

        num_xs = len(x.columns)
        palette = seaborn.color_palette(kwargs["palette"], num_xs).as_hex()

        if num_xs != len(y.columns):

            raise ValueError("If y values are dataframe, number of y columns needs to equal number of x columns. "
                             "If y is the same value repeated for each x then pass y as a series")

        ys = y.values.flatten()
        xs = x.values.flatten()
        colors = palette * (len(xs)/len(palette))

    elif isinstance(y, pd.DataFrame) and isinstance(x, pd.Series):

        num_ys = len(y.columns)
        palette = seaborn.cubehelix_palette(num_ys).as_hex()

        xs = x.repeat(num_ys).values
        ys = y.values.flatten()

        colors = palette * (len(ys)/len(palette))

    elif isinstance(y, pd.Series) and isinstance(x, pd.Series):

        palette = seaborn.cubehelix_palette(1).as_hex()

        xs = x.tolist()
        ys = y.tolist()
        colors = palette * len(ys)

    else:

        raise ValueError

    p = figure(plot_width=kwargs["plot_width"], plot_height=kwargs["plot_height"])
    source = ColumnDataSource(data=dict(x=xs, y=ys, color=colors))
    sc = p.scatter('x', 'y', color="color", source=source)

    def callback(source=source, sc=sc, window=None):

        f = cb_obj.value
        sc.glyph.size = f
        source.change.emit()

    dot_size_slider = Slider(start=0, end=50, value=1, step=1, title="Stuff", callback=CustomJS.from_py_func(callback))

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components({"p": p, "dot_size_slider": dot_size_slider}, INLINE)

    return script, div, js_resources, css_resources

if __name__ == '__main__':

    df = pd.DataFrame(np.random.randn(10, 3), columns=["x1", "x2", "y"])

    plot_scatter(df[["x1", "x2"]], df["y"], palette="GnBu_d", plot_width=600, plot_height=600)
