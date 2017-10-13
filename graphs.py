import seaborn
import numpy as np
from bokeh.plotting import figure, curdoc
from bokeh.models import CustomJS, Slider, ColumnDataSource, Palette, Select, ColorMapper, TextInput, Line, Legend
from bokeh.client import push_session, ClientSession
from bokeh.models.glyphs import VBar
from bokeh.models.renderers import GlyphRenderer
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

        if self.group is not None:

            self.x = x
            self.y = y

            self.num_colors = len(set(self.group))

            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs["palette"]]
            temp_df = pd.DataFrame(list(zip(self.x, self.y, self.group)),
                                   columns=["x", "y", "group"])
            temp_group = temp_df.groupby("group", as_index=False)

            self.num_mod = floor(len(self.group) / len(self.palette))
            self.colors = self.palette * self.num_mod

            self.source = {}

            for g in temp_group.groups:

                tg = temp_group.get_group(g)

                self.source.update({g: ColumnDataSource(data=dict(x=tg["x"].tolist(), y=tg["y"].tolist(),
                                                                  group=[g, ]*len(tg.x.index),
                                                                  color=[self.palette[
                                                                             list(temp_group.groups.keys()).index(g)],]
                                                                        *len(tg.index)))})
        else:

            if y.size != x.size:

                if y.size % x.size == 0 or x.size % y.size == 0:

                    if x.size > y.size:

                        self.x = x.values.flatten()
                        self.y = y.repeat(x.size/y.size).values

                    elif y.size > x.size:

                        self.y = y.values.flatten()
                        self.x = x.repeat(y.size / x.size).values

                    self.palettes = self.palette_maps(1)
                    self.palette = self.palettes[kwargs["palette"]]
                    self.colors = self.palette * len(self.y)

                    self.source = ColumnDataSource(data=dict(x=self.x, y=self.y, color=self.colors))

                else:

                    raise AttributeError("data provided in columns x and y need to have the same dimensions or be"
                                         " divisible.")
            else:

                self.x = x
                self.y = y
                self.palettes = self.palette_maps(1)
                self.palette = self.palettes[kwargs["palette"]]
                self.colors = self.palette * len(self.y)

                self.source = ColumnDataSource(data=dict(x=self.x, y=self.y, color=self.colors))

        self.graph = None
        self.p = None

    def palette_maps(self, n_colors):

        palette_map = {}

        for n in pyplot.colormaps():

            if n == "jet":

                continue

            palette_map.update({n: seaborn.color_palette(n, n_colors).as_hex()})

        return palette_map

    def change_palette_lines(self, attr, old, new):

        self.palette = self.palettes[new]

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:
            ds = r.data_source

            self.colors = [self.palette[renderer.index(r)], ] * len(ds.data["color"])
            r.glyph.line_color = self.colors[0]
            # curdoc().add_next_tick_callback(partial(self.update, x=ds.data["x"], y=ds.data["y"], c=self.colors,
            #                                         g=ds.data["group"], source=ds))

    def change_palette_scatter(self, attr, old, new):
        self.palette = self.palettes[new]

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:
            ds = r.data_source

            self.colors = [self.palette[renderer.index(r)], ] * len(ds.data["color"])
            r.glyph.fill_color = self.colors[0]
            r.glyph.line_color = self.colors[0]

    def change_palette_bar(self, attr, old, new):

        self.palette = self.palettes[new]

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:
            ds = r.data_source

            self.colors = [self.palette[renderer.index(r)], ] * len(ds.data["color"])
            r.glyph.fill_color = self.colors[0]

    def change_dot_size(self, attr, old, new):

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]
        for r in renderer:

            r.glyph.size = new

    def change_line_thick(self, attr, old, new):

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]
        for r in renderer:

            r.glyph.line_width = new


    def change_figure_title(self, attr, old, new):

        self.p.title.text = new

    def update(self, x, y, c, g=None, source=None):

        # if not self.series:

        if source:

            source.data["color"] = []
            source.data["x"] = []
            source.data["y"] = []

        else:

            self.source.data["color"] = []
            self.source.data["x"] = []
            self.source.data["y"] = []

        if self.group is not None:

            if source:

                source.data["group"] = []
                source.stream(dict(x=x, y=y, color=c, group=g))

            else:

                self.source.data["group"] = []
                self.source.stream(dict(x=x, y=y, color=c, group=g))

        else:

            if source:

                source.stream(dict(x=x, y=y, color=c))

            else:

                self.source.stream(dict(x=x, y=y, color=c))

    def plot_scatter(self):

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height)

        if self.group is not None:

            for k in self.source.keys():

                self.p.scatter("x", "y", color="color", source=self.source[k])

        else:

            self.graph = self.p.scatter('x', 'y', color="color", source=self.source)

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        title_text = TextInput(placeholder="Figure Title")

        dot_size_slider = Slider(start=1, end=100, value=1, step=1, title="Dot Size")
        dot_size_slider.on_change("value", self.change_dot_size)
        select_pal.on_change("value", self.change_palette_scatter)
        title_text.on_change("value", self.change_figure_title)

        app_layout = layout([[title_text],
                             [self.p],
                             [select_pal],
                             [dot_size_slider]])
        return app_layout

    def plot_bar(self):

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height)


        if self.group is not None:

            for g in self.source.keys():

                if list(self.source.keys()).index(g) % 2 == 0:

                    self.source[g].data["x"] = [x + .2*list(self.source.keys()).index(g) for x in self.source[g].data["x"]]

                else:
                    self.source[g].data["x"] = [x - .2 * list(self.source.keys()).index(g) for x in
                                                self.source[g].data["x"]]

                self.p.vbar(x="x", top="y", width=.5, fill_color="color", source=self.source[g],
                            line_color="black")

        else:

            self.p.vbar(x="x", top="y", width=.5, fill_color="color", source=self.source, line_color="black")

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])

        select_pal.on_change("value", self.change_palette_bar)

        app_layout = layout([[select_pal],
                            [self.p]])

        return app_layout

    def plot_line(self):

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height)
        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        line_thick_slider = Slider(start=1, end=10, value=1, step=1, title="Line Width")
        title_text = TextInput(placeholder="Figure Title")

        if self.group is not None:

            for k in self.source.keys():

                self.p.line("x", "y", color=self.source[k].data["color"][0], source=self.source[k])

        else:

            self.p.line("x", "y", color=self.source.data["color"][0], source=self.source)

        select_pal.on_change("value", self.change_palette_lines)
        line_thick_slider.on_change("value", self.change_line_thick)
        title_text.on_change("value", self.change_figure_title)


        app_layout = layout([select_pal],
                            [title_text],
                            [self.p],
                            [line_thick_slider])
        return app_layout



