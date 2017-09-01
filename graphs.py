import seaborn
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.models import CustomJS, Slider, ColumnDataSource, Palette, Select, ColorMapper, TextInput
from bokeh.client import push_session, ClientSession
from bokeh.models.glyphs import VBar
from matplotlib import pyplot
from bokeh.layouts import layout, row
from math import floor, ceil

from functools import partial
import pandas as pd


class GraphPlot:

    def __init__(self, x, y, **kwargs):

        self.plot_width = kwargs["plot_width"]
        self.plot_height = kwargs["plot_height"]

        try:

            self.group = kwargs["group"]

        except KeyError:

            self.group = None

        if isinstance(y, pd.Series) and isinstance(x, pd.DataFrame):

            self.series = False

            # if not self.group:
            self.num_colors = len(x.columns)
            # else:
            #     self.num_colors = len(self.group)

            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]

            self.ys = y.repeat(self.num_colors).values
            self.xs = x.values.flatten()
            self.num_mod = floor(len(self.xs) / len(self.palette))
            self.colors = self.palette * self.num_mod

        elif isinstance(y, pd.DataFrame) and isinstance(x, pd.DataFrame):

            self.series = False
            self.num_colors = len(x.columns)
            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]

            if self.num_colors != len(y.columns):

                raise ValueError("If y values are dataframe, number of y columns needs to equal number of x columns. "
                                 "If y is the same value repeated for each x then pass y as a series")

            self.ys = y.values.flatten()
            self.xs = x.values.flatten()
            self.num_mod = floor(len(self.xs) / len(self.palette))
            self.colors = self.palette * self.num_mod

        elif isinstance(y, pd.DataFrame) and isinstance(x, pd.Series):

            self.series = False
            self.num_colors = len(y.columns)
            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]

            self.xs = x.repeat(self.num_colors).values
            self.ys = y.values.flatten()

            self.num_mod = floor(len(self.ys) / len(self.palette))
            self.colors = self.palette * self.num_mod

        elif isinstance(y, pd.Series) and isinstance(x, pd.Series):

            self.series = True
            self.palettes = self.palette_maps(1)
            self.palette = self.palettes[kwargs["palette"]]
            self.num_colors = 1

            self.xs = x.tolist()
            self.ys = y.tolist()
            self.num_mod = len(self.palette) * len(self.ys)
            self.colors = self.palette * self.num_mod
            print(self.colors)

        else:

            raise ValueError

        self.source = ColumnDataSource(data=dict(x=self.xs, y=self.ys, color=self.colors))
        self.col_source = ColumnDataSource(data=self.palettes)

        self.graph = None
        self.p = None

    def palette_maps(self, n_colors):

        palette_map = {}

        for n in pyplot.colormaps():

            if n == "jet":

                continue

            palette_map.update({n: seaborn.color_palette(n, n_colors).as_hex()})

        return palette_map

    def change_palette(self, attr, old, new):
        self.palette = self.palettes[new]

        self.colors = self.palette * self.num_mod
        curdoc().add_next_tick_callback(partial(self.update, x=self.xs, y=self.ys, c=self.colors))

    def change_dot_size(self, attr, old, new):

        self.graph.glyph.size = new
        curdoc().add_next_tick_callback(partial(self.update, x=self.xs, y=self.ys, c=self.colors))

    def change_figure_title(self, attr, old, new):

        print(self.p.title)
        self.p.title.text = new
        self.update(self.source.data["x"], self.source.data["y"], self.source.data["color"])

    def update(self, x, y, c):

        # if not self.series:
        self.source.data["color"] = []
        self.source.data["x"] = []
        self.source.data["y"] = []
        self.source.stream(dict(x=x, y=y, color=c))

    def plot_scatter(self):

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height)

        self.graph = self.p.scatter('x', 'y', color="color", source=self.source)

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        title_text = TextInput(placeholder="Figure Title")

        dot_size_slider = Slider(start=1, end=100, value=1, step=1, title="Dot Size")
        dot_size_slider.on_change("value", self.change_dot_size)
        select_pal.on_change("value", self.change_palette)
        title_text.on_change("value", self.change_figure_title)

        app_layout = layout([[title_text],
                             [self.p],
                             [select_pal],
                             [dot_size_slider]])
        return app_layout

    def plot_bar(self):

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height)
        self.graph = self.p.vbar(x="x", top="y", width=.5, fill_color="color", source=self.source, line_color="black")

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])

        select_pal.on_change("value", self.change_palette)

        app_layout = layout([[select_pal],
                            [self.p]])

        return app_layout


df = pd.DataFrame(np.random.randn(10, 4), columns=["x1", "x2", "y1", "y2"])
gp = GraphPlot(df[["x1", "x2"]], df["y1"], palette="Accent", plot_width=600, plot_height=600)

app_layout = gp.plot_scatter()

doc = curdoc()
doc.add_root(app_layout)
