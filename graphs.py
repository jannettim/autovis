import seaborn
from collections import OrderedDict
from bokeh.plotting import figure, curdoc
from bokeh.models import Slider, ColumnDataSource, Select, TextInput, Legend, CheckboxGroup, Button
from bokeh.models.renderers import GlyphRenderer
from matplotlib import pyplot
from bokeh.layouts import layout, row, Spacer
from math import floor, ceil
import pandas as pd
from sklearn import datasets
from stats import get_regression_line

# from file_input import ImportData
# from functools import partial


class GraphPlot:
    """
    Basic plotting routine. Takes dataframe and turns it into plotable. Outputs plot
    """

    def __init__(self, x, y, **kwargs):
        """
        :param x: x-axis points
        :param y: y-axis points
        :param kwargs: plotting attributes
        """

        # Get values or defaults for plotting attributes
        self.x_axis_type = kwargs.get("x_axis_type", "linear")
        self.plot_title = kwargs.get("plot_title", " ")
        self.group = kwargs.get("group", None)
        self.x_axis_label = kwargs.get("x_axis_label", None)
        self.y_axis_label = kwargs.get("y_axis_label", None)
        self.plot_width = kwargs.get("plot_width", 600)
        self.plot_height = kwargs.get("plot_height", 600)

        self.file_source = ColumnDataSource({'file_contents': [], 'file_name': []})

        if self.group is not None:

            self.x = x
            self.y = y

            # Gets the number of groups
            self.num_colors = len(set(self.group))

            # Get the colors for the groups and assign then
            self.palettes = self.palette_maps(self.num_colors)
            self.palette = self.palettes[kwargs.get("palette", "Accent")]
            temp_df = pd.DataFrame(list(zip(self.x, self.y, self.group)),
                                   columns=["x", "y", "group"])
            temp_group = temp_df.groupby("group", as_index=False)

            self.num_mod = floor(len(self.group) / len(self.palette))
            self.colors = self.palette * self.num_mod

            self.source = OrderedDict()

            for g in temp_group.groups:

                tg = temp_group.get_group(g)

                self.source.update({str(g): ColumnDataSource(data=dict(x=tg["x"].tolist(), y=tg["y"].tolist(),
                                                                  group=[g, ]*len(tg.x.index),
                                                                  color=[self.palette[
                                                                             list(temp_group.groups.keys()).index(g)],]
                                                                        *len(tg.index)))})
        else:

            # if y or x is not equal, 1 will be repeated

            if y.size != x.size:

                # repeats the smaller column/list/array
                if y.size % x.size == 0 or x.size % y.size == 0:

                    if x.size > y.size:

                        self.x = x.values.flatten()
                        self.y = y.repeat(x.size/y.size).values

                    elif y.size > x.size:

                        self.y = y.values.flatten()
                        self.x = x.repeat(y.size / x.size).values

                    self.palettes = self.palette_maps(1)
                    self.palette = self.palettes[kwargs.get("palette", "Accent")]
                    self.colors = self.palette * len(self.y)

                    self.source = ColumnDataSource(data=dict(x=self.x, y=self.y, color=self.colors))

                else:

                    raise AttributeError("data provided in columns x and y need to have the same dimensions or be"
                                         " divisible.")
            else:

                self.x = x
                self.y = y
                self.palettes = self.palette_maps(1)
                self.palette = self.palettes[kwargs.get("palette", "Accent")]
                self.colors = self.palette * len(self.y)

                self.source = ColumnDataSource(data=dict(x=self.x, y=self.y, color=self.colors))

        self.graph = None
        self.p = None
        self.hist_source = None

    def palette_maps(self, n_colors):

        """
        Creates the palettes from seaborn for a given number of groups

        :param n_colors: number of colors to assign
        :return: map of palette names to hex codes
        """

        palette_map = {}

        for n in pyplot.colormaps():

            if n == "jet":

                continue

            palette_map.update({n: seaborn.color_palette(n, n_colors).as_hex()})

        return palette_map

    def change_palette_lines(self, attr, old, new):

        """
        Changes the color palette for lines

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        # get new palette colors
        self.palette = self.palettes[new]

        # get glyphs
        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        # assign colors to renderers
        for r in renderer:
            ds = r.data_source

            self.colors = [self.palette[renderer.index(r)], ] * len(ds.data["color"])
            r.glyph.line_color = self.colors[0]

    def change_palette_scatter(self, attr, old, new):
        """
        Change palette for scatter plots

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        self.palette = self.palettes[new]

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:

            ds = r.data_source

            temp_palette = []

            for p in self.palette:

                temp_palette.extend([p, ] * 3)

            try:
                self.colors = [temp_palette[renderer.index(r)], ] * len(ds.data["color"])

            except KeyError:

                if r.name == "reg_line":

                    r.glyph.line_color = [temp_palette[renderer.index(r)], ][0]

                if r.name == "error":
                    r.glyph.fill_color = [temp_palette[renderer.index(r)], ][0]
                    r.glyph.line_color = [temp_palette[renderer.index(r)], ][0]

            if r.name != "reg_line" and r.name != "error":
                ds.data["color"] = self.colors

    def change_palette_hist(self, attr, old, new):
        """
        Change palette for histograms

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        self.palette = self.palettes[new]

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:

            ds = r.data_source
            self.colors = [(self.palette*3)[renderer.index(r)], ] * len(ds.data["color"])

            ds.data["color"] = self.colors

    def change_hist_line(self, attr, old, new):

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:

            ds = r.data_source

            if new == [0]:

                r.glyph.line_color = "black"

            else:
                r.glyph.line_color = ds.data["color"][0]

    def change_bins(self, attr, old, new):

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        if self.group is not None:

            for r in renderer:

                self.p.renderers.remove(r)

            for k in self.source.keys():

                cuts = pd.Series(pd.cut(self.source[k].data["x"], new)).str.replace("\(|\]", "").str.split(", ", expand=True).astype(float)
                cuts["y"] = self.source[k].data["y"]

                cuts = cuts.groupby([0, 1], as_index=False)["y"].size().reset_index(name="freq")

                self.hist_source= ColumnDataSource(data=dict(min=cuts[0].tolist(), max=cuts[1].tolist(),
                                                             freq=cuts["freq"].tolist(),
                                                             color=[self.source[k].data["color"][0], ] * len(cuts.index)))

                self.p.quad(left="min", right="max", bottom=0, top="freq", source=self.hist_source, line_color="black",
                            color="color")

    def change_palette_bar(self, attr, old, new):

        self.palette = self.palettes[new]

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:
            ds = r.data_source

            self.colors = [self.palette[renderer.index(r)], ] * len(ds.data["color"])
            r.glyph.fill_color = self.colors[0]

    def change_dot_size(self, attr, old, new):

        """
        Changes the size of the dots in scatter plots

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]
        for r in renderer:

            try:
                r.glyph.size = new

            except AttributeError:

                pass

    def change_line_thick(self, attr, old, new):
        """
        Changes the thickness of the lines in line graphs
        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]
        for r in renderer:

            r.glyph.line_width = new

    def change_figure_title(self, attr, old, new):

        """
        Change the figure title

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        self.p.title.text = new

    def change_figure_yaxis(self, attr, old, new):

        """
        Change the figure title

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        self.p.yaxis.axis_label = new

    def change_figure_xaxis(self, attr, old, new):

        """
        Change the figure title

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        self.p.xaxis.axis_label = new

    def change_glyph_alpha(self, attr, old, new):
        """
        Change the transparency of glyphs

        :param attr: attribute changes
        :param old: old value
        :param new: new value
        :return: None
        """

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        for r in renderer:

            try:
                if r.name == "error":

                    r.glyph.fill_alpha = new*.2

                else:
                    r.glyph.fill_alpha = new

            except AttributeError:
                pass

    def add_regression(self, attr, old, new):

        if new:

            self.reg_err_check.disabled = False

            renderer = [r for r in self.p.renderers if r.name == "reg_line"]
            for r in renderer:

                r.visible = True

        else:

            renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

            for r in renderer:

                if r.name == "reg_line" or r.name == "error":

                    r.visible = False

            self.reg_err_check.active = [1]
            self.reg_err_check.disabled = True

    def add_reg_error(self, attr, old, new):

        renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

        if new == [0]:

            for r in renderer:

                if r.name == "error":

                    r.visible = True
        else:

            for r in renderer:

                if r.name == "error":

                    r.visible = False

    def update(self, x, y, c, g=None, source=None):
        """
        Update new values on plot

        :param x: x values
        :param y: y values
        :param c: colors
        :param g: groups
        :param source: data source
        :return: None
        """

        # remove existing data
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
                # reassign
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
        """
        Plot scatter plots

        :return: None
        """

        # set figure
        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height,
                        x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label)

        y_axis_label = TextInput(placeholder="y-axis label")
        x_axis_label = TextInput(placeholder="x-axis label")

        # handle groups
        if self.group is not None:

            # plot each line
            for k in self.source.keys():

                self.p.scatter("x", "y", color="color", source=self.source[k])
                reg_x, reg_y, pred_upper, pred_lower = get_regression_line(self.source[k].data["x"],
                                                                           self.source[k].data["y"])

                self.p.line(reg_x, reg_y, name="reg_line", color=self.source[k].data["color"][0])

                bands = sorted(list(zip(pred_upper.tolist(), pred_lower.tolist(), reg_x)), key=lambda z: z[2])
                band_x = [t[2] for t in bands] + [t[2] for t in bands][::-1]
                bounds = [t[1] for t in bands] + [t[0] for t in bands][::-1]

                self.p.patch(band_x, bounds, color=self.source[k].data["color"][0], alpha=.2, name="error")
                rends = [r for r in self.p.renderers]

                for r in rends:

                    if r.name in ["reg_line", "error"]:

                        r.visible = False

            legend = Legend(items=[*list(zip(list(self.source.keys()),
                                             [[r] for r in self.p.renderers if isinstance(r, GlyphRenderer)
                                              and r.name not in ["reg_line", "error"]]))],
                            location=(0, -30))

            self.p.add_layout(legend, 'left')

        else:

            self.p.scatter('x', 'y', color="color", source=self.source)

            reg_x, reg_y, pred_upper, pred_lower = get_regression_line(self.source.data["x"], self.source.data["y"])

            self.p.line(reg_x, reg_y, name="reg_line", color=self.source.data["color"][0])

            bands = sorted(list(zip(pred_upper.tolist(), pred_lower.tolist(), reg_x)), key=lambda z: z[2])
            band_x = [t[2] for t in bands] + [t[2] for t in bands][::-1]
            bounds = [t[1] for t in bands] + [t[0] for t in bands][::-1]

            self.p.patch(band_x, bounds, color=self.source[k].data["color"][0], alpha=.2, name="error")
            rends = [r for r in self.p.renderers]

            for r in rends:

                if r.name in ["reg_line", "error"]:

                    r.visible = False

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        title_text = TextInput(placeholder="Figure Title")

        dot_size_slider = Slider(start=1, end=100, value=1, step=1, title="Dot Size")
        alpha_slider = Slider(start=0, end=1, value=1, step=.01, title="Transparency")
        reg_check = CheckboxGroup(labels=["Regression Line"])
        self.reg_err_check = CheckboxGroup(labels=["Error Region"], disabled=True)

        dot_size_slider.on_change("value", self.change_dot_size)
        select_pal.on_change("value", self.change_palette_scatter)
        title_text.on_change("value", self.change_figure_title)
        alpha_slider.on_change("value", self.change_glyph_alpha)

        reg_check.on_change("active", self.add_regression)
        self.reg_err_check.on_change("active", self.add_reg_error)
        y_axis_label.on_change("value", self.change_figure_yaxis)
        x_axis_label.on_change("value", self.change_figure_xaxis)

        app_layout = layout([[title_text],
                             [y_axis_label, self.p],
                             [Spacer(height=10, width=500), x_axis_label],
                             [select_pal],
                             [dot_size_slider],
                             [alpha_slider],
                             [reg_check, self.reg_err_check]])

        return app_layout

    def plot_bar(self):
        """
        Plot bar chart

        :return:
        """

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height, x_axis_label=self.x_axis_label,
                        y_axis_label=self.y_axis_label)

        y_axis_label = TextInput(placeholder="y-axis label")
        x_axis_label = TextInput(placeholder="x-axis label")

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
        title_text = TextInput(placeholder="Figure Title")

        select_pal.on_change("value", self.change_palette_bar)
        y_axis_label.on_change("value", self.change_figure_yaxis)
        x_axis_label.on_change("value", self.change_figure_xaxis)
        title_text.on_change("value", self.change_figure_title)

        app_layout = layout([[select_pal],
                             [title_text],
                             [y_axis_label, self.p],
                             [Spacer(height=10, width=500), x_axis_label],])

        return app_layout

    def plot_line(self):
        """
        Plot line graph

        :return:
        """

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height, x_axis_type=self.x_axis_type,
                        x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label, title=self.plot_title)

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        line_thick_slider = Slider(start=1, end=10, value=1, step=1, title="Line Width")
        title_text = TextInput(placeholder="Figure Title")
        y_axis_label = TextInput(placeholder="y-axis label")
        x_axis_label = TextInput(placeholder="x-axis label")

        if self.group is not None:

            for k in self.source.keys():

                self.p.line("x", "y", color=self.source[k].data["color"][0], source=self.source[k])

            legend = Legend(items=[*list(zip(list(self.source.keys()),
                                             [[r] for r in self.p.renderers if isinstance(r, GlyphRenderer)]))],
                            location=(0, -30))
            self.p.yaxis[0].formatter.use_scientific = False
            self.p.add_layout(legend, 'left')

        else:

            self.p.line("x", "y", color=self.source.data["color"][0], source=self.source)

        select_pal.on_change("value", self.change_palette_lines)
        line_thick_slider.on_change("value", self.change_line_thick)
        title_text.on_change("value", self.change_figure_title)
        y_axis_label.on_change("value", self.change_figure_yaxis)
        x_axis_label.on_change("value", self.change_figure_xaxis)

        app_layout = layout([select_pal],
                            [title_text],
                            [y_axis_label, self.p],
                            [Spacer(height=10, width=500), x_axis_label],
                            [line_thick_slider])
        return app_layout

    def plot_histogram(self, bins):

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height, x_axis_type=self.x_axis_type,
                        x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label, title=self.plot_title)

        if self.group is not None:

            for k in self.source.keys():

                cuts = pd.Series(pd.cut(self.source[k].data["x"], bins)).str.replace("\(|\]", "").str.split(", ", expand=True).astype(float)
                cuts["y"] = self.source[k].data["y"]

                cuts = cuts.groupby([0, 1], as_index=False)["y"].size().reset_index(name="freq")

                self.hist_source = ColumnDataSource(data=dict(min=cuts[0].tolist(), max=cuts[1].tolist(),
                                                         freq=cuts["freq"].tolist(),
                                                         color=[self.source[k].data["color"][0], ] * len(cuts.index)))

                self.p.quad(left="min", right="max", bottom=0, top="freq", source=self.hist_source, line_color="black",
                            color="color")

        else:

            cuts = pd.cut(self.source.data["x"], bins).str.replace("\(|\]", "").str.split(", ", expand=True).astype(float)
            cuts["y"] = self.source.data["y"]

            cuts = cuts.groupby([0, 1], as_index=False)["y"].size().reset_index(name="freq")

            self.hist_source = ColumnDataSource(data=dict(min=cuts[0].tolist(), max=cuts[1].tolist(),
                                                     freq=cuts["freq"].tolist(),
                                                     color=[self.source.data["color"][0], ] * len(cuts.index)))

            self.p.quad(left="min", right="max", bottom=0, top="freq", source=self.hist_source, line_color="black",
                        color="color")

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        alpha_slider = Slider(start=0, end=1, value=1, step=.01, title="Transparency")
        title_text = TextInput(placeholder="Figure Title")
        bins_slider = Slider(start=1, end=99, value=bins, step=1, title="Bins")
        line_check = CheckboxGroup(labels=["Outline"], active=[0])
        y_axis_label = TextInput(placeholder="y-axis label")
        x_axis_label = TextInput(placeholder="x-axis label")

        select_pal.on_change("value", self.change_palette_hist)
        alpha_slider.on_change("value", self.change_glyph_alpha)
        title_text.on_change("value", self.change_figure_title)
        y_axis_label.on_change("value", self.change_figure_yaxis)
        x_axis_label.on_change("value", self.change_figure_xaxis)
        line_check.on_change("active", self.change_hist_line)
        bins_slider.on_change("value", self.change_bins)

        app_layout = layout([title_text],
                            [select_pal],
                            [y_axis_label, self.p],
                            [Spacer(height=10, width=500), x_axis_label],
                            [alpha_slider],
                            [bins_slider],
                            [line_check])

        return app_layout


# df = pd.read_csv("iris.csv")
#
# gp = GraphPlot(df["Sepal_Length"], df["Sepal_Width"], group=df["Species"])#, group=df["Tests Failed"])#, x_axis_type="datetime")
#
# app_layout = gp.plot_histogram(7)
# app_layout = gp.plot_scatter()


# doc = curdoc()
# doc.add_root(app_layout)