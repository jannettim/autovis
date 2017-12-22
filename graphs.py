import seaborn
from collections import OrderedDict
from bokeh.plotting import figure, curdoc
from bokeh.models import Slider, ColumnDataSource, Select, TextInput, Legend, CheckboxGroup
from bokeh.models.renderers import GlyphRenderer
from matplotlib import pyplot
from bokeh.layouts import layout
from math import floor, ceil
import pandas as pd
from sklearn import datasets
from stats import get_regression_line


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

            try:
                self.colors = [self.palette[renderer.index(r)], ] * len(ds.data["color"])
            except IndexError:
                self.colors = [self.palette[int(renderer.index(r)-(len(renderer)/2))], ] * len(ds.data["color"])

            try:
                r.glyph.fill_color = self.colors[0]

            except AttributeError:

                pass
            r.glyph.line_color = self.colors[0]

            ds.data["color"] = self.colors

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
                r.glyph.fill_alpha = new

            except AttributeError:
                pass

    def add_regression(self, attr, old, new):

        if new:
            if self.group is not None:

                for k in self.source.keys():

                    reg_x, reg_y, pred_upper, pred_lower = get_regression_line(self.source[k].data["x"],
                                                                               self.source[k].data["y"])

                    temp_source = ColumnDataSource(data=dict(x=reg_x, y=reg_y, color=self.source[k].data["color"]))
                    self.p.line("x", "y", line_color=temp_source.data["color"][0], source=temp_source, name="reg")

                    # test = sorted(list(zip(pred_upper.tolist(), pred_lower.tolist(), reg_x)), key=lambda z: z[2])
                    # band_x = [t[2] for t in test] + [t[2] for t in test][::-1]
                    # bounds = [t[1] for t in test] + [t[0] for t in test][::-1]
                    #
                    # patch_source = ColumnDataSource(data=dict(x=band_x, y=bounds, color=self.source[k].data["color"] * 2))
                    #
                    # self.p.patch("x", "y", color=patch_source.data["color"][0], alpha=.5, source=patch_source)

            else:

                pass

        else:

            renderer = [r for r in self.p.renderers if isinstance(r, GlyphRenderer)]

            for r in renderer:

                if r.name == "reg":

                    self.p.renderers.remove(r)

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
        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height)

        # handle groups
        if self.group is not None:

            # plot each line
            for k in self.source.keys():

                self.p.scatter("x", "y", color="color", source=self.source[k])

        else:

            self.p.scatter('x', 'y', color="color", source=self.source)

        legend = Legend(items=[*list(zip(list(self.source.keys()),
                                         [[r] for r in self.p.renderers if isinstance(r, GlyphRenderer)]))],
                        location=(0, -30))

        self.p.add_layout(legend, 'left')

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        title_text = TextInput(placeholder="Figure Title")

        dot_size_slider = Slider(start=1, end=100, value=1, step=1, title="Dot Size")
        alpha_slider = Slider(start=0, end=1, value=1, step=.01, title="Transparency")
        reg_check = CheckboxGroup(labels=["Regression Line"])

        dot_size_slider.on_change("value", self.change_dot_size)
        select_pal.on_change("value", self.change_palette_scatter)
        title_text.on_change("value", self.change_figure_title)
        alpha_slider.on_change("value", self.change_glyph_alpha)

        reg_check.on_change("active", self.add_regression)

        app_layout = layout([[title_text],
                             [self.p],
                             [select_pal],
                             [dot_size_slider],
                             [alpha_slider],
                             reg_check])

        return app_layout

    def plot_bar(self):
        """
        Plot bar chart

        :return:
        """

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
        """
        Plot line graph

        :return:
        """

        self.p = figure(plot_width=self.plot_width, plot_height=self.plot_height, x_axis_type=self.x_axis_type,
                        x_axis_label=self.x_axis_label, y_axis_label=self.y_axis_label, title=self.plot_title)

        select_pal = Select(options=[c for c in pyplot.colormaps() if c != "jet"])
        line_thick_slider = Slider(start=1, end=10, value=1, step=1, title="Line Width")
        title_text = TextInput(placeholder="Figure Title")

        if self.group is not None:

            for k in self.source.keys():

                self.p.line("x", "y", color=self.source[k].data["color"][0], source=self.source[k])

        else:

            self.p.line("x", "y", color=self.source.data["color"][0], source=self.source)

        legend = Legend(items=[*list(zip(list(self.source.keys()),
                                         [[r] for r in self.p.renderers if isinstance(r, GlyphRenderer)]))],
                        location=(0, -30))
        self.p.yaxis[0].formatter.use_scientific = False

        select_pal.on_change("value", self.change_palette_lines)
        line_thick_slider.on_change("value", self.change_line_thick)
        title_text.on_change("value", self.change_figure_title)

        self.p.add_layout(legend, 'left')

        app_layout = layout([select_pal],
                            [title_text],
                            [self.p],
                            [line_thick_slider])
        return app_layout

iris = datasets.load_iris()

df = pd.DataFrame(iris.data, columns=["Sepal_Length", "Sepal_Width", "Petal_Length", "Petal_Width"])
df["Species"] = iris.target

gp = GraphPlot(x=df["Sepal_Length"], y=df["Sepal_Width"], group=df["Species"], plot_height=600, plot_width=1000)
app_layout = gp.plot_scatter()

curdoc().add_root(app_layout)
