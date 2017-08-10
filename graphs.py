import seaborn
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.models import CustomJS, Slider, ColumnDataSource, Palette, Select, ColorMapper
from bokeh.client import push_session, ClientSession
from matplotlib import pyplot
from bokeh.layouts import layout, row
from math import floor, ceil

from functools import partial
import pandas as pd


class GraphPlot:

    def __init__(self, x, y, **kwargs):

        self.plot_width = kwargs["plot_width"]
        self.plot_height = kwargs["plot_height"]
        # self.doc = kwargs["doc"]
        # self.session = kwargs["session"]

        if isinstance(y, pd.Series) and isinstance(x, pd.DataFrame):
            self.num_colors = len(x.columns)
            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]

            self.ys = y.repeat(self.num_colors).values
            self.xs = x.values.flatten()
            self.group = floor(len(self.xs)/len(self.palette))
            self.colors = self.palette * self.group
            print(self.colors)

        elif isinstance(y, pd.DataFrame) and isinstance(x, pd.DataFrame):

            self.num_colors = len(x.columns)
            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]

            if self.num_colors != len(y.columns):

                raise ValueError("If y values are dataframe, number of y columns needs to equal number of x columns. "
                                 "If y is the same value repeated for each x then pass y as a series")

            self.ys = y.values.flatten()
            self.xs = x.values.flatten()
            self.group = floor(len(self.xs)/len(self.palette))
            self.colors = self.palette * self.group

        elif isinstance(y, pd.DataFrame) and isinstance(x, pd.Series):

            self.num_colors = len(y.columns)
            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]

            self.xs = x.repeat(self.num_colors).values
            self.ys = y.values.flatten()

            self.group = floor(len(self.ys)/len(self.palette))
            self.colors = self.palette * self.group

        elif isinstance(y, pd.Series) and isinstance(x, pd.Series):

            self.palettes = self.palette_maps(1)
            self.palette = self.palettes[kwargs["palette"]]
            self.num_colors = 1

            self.xs = x.tolist()
            self.ys = y.tolist()
            self.group = self.palette * len(self.ys)
            self.colors = self.palette * self.group

        else:

            raise ValueError

        self.source = ColumnDataSource(data=dict(x=self.xs, y=self.ys, color=self.colors))
        self.col_source = ColumnDataSource(data=self.palettes)

        self.graph = None

    def palette_maps(self, n_colors):

        palette_map = {}

        for n in pyplot.colormaps():

            if n == "jet":

                continue

            palette_map.update({n: seaborn.color_palette(n, n_colors).as_hex()})

        return palette_map

    def change_palette(self, attr, old, new):
        self.palette = self.palettes[new]

        self.colors = self.palette * self.group
        curdoc().add_next_tick_callback(partial(self.update, x=self.xs, y=self.ys, c=self.colors))

    def change_dot_size(self, attr, old, new):

        self.graph.glyph.size = new
        curdoc().add_next_tick_callback(partial(self.update, x=self.xs, y=self.ys, c=self.colors))

    def update(self, x, y, c):

        self.source.data["color"] = []
        self.source.stream(dict(x=x, y=y, color=c))

    def plot_scatter(self):

        p = figure(plot_width=self.plot_width, plot_height=self.plot_height)

        self.graph = p.scatter('x', 'y', color="color", source=self.source)

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])

        dot_size_slider = Slider(start=1, end=100, value=1, step=1, title="Dot Size")
        dot_size_slider.on_change("value", self.change_dot_size)
        select_pal.on_change("value", self.change_palette)

        app_layout = layout([[select_pal],
                             [p],
                             [dot_size_slider]])

        # curdoc().add_root(app_layout)
        #
        return app_layout


# def main(doc):
#
#     df = pd.DataFrame(np.random.randn(10, 4), columns=["x1", "x2", "y1", "y2"])
#     gp = GraphPlot(df[["x1", "x2"]], df[["y1", "y2"]], palette="Accent", plot_width=600, plot_height=600)
#
#     app_layout = gp.plot_scatter()
#
#     doc.add_root(app_layout)


df = pd.DataFrame(np.random.randn(10, 4), columns=["x1", "x2", "y1", "y2"])
gp = GraphPlot(df[["x1", "x2"]], df[["y1", "y2"]], palette="Accent", plot_width=600, plot_height=600)# , doc=doc,
               # session=session)

app_layout = gp.plot_scatter()

doc = curdoc()
doc.add_root(app_layout)

# session = push_session(doc)
# session.show()
# session.loop_until_closed()