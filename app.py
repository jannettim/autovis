from flask import Flask, render_template, request
import graphs
from bokeh.util.string import encode_utf8
import pandas as pd
import numpy as np
from matplotlib import pyplot

app = Flask(__name__)


def getitem(obj, item, default):

    if item not in obj:
        return default

    else:
        return obj[item]

def list_palettes():

    return pyplot.colormaps()


@app.route("/", methods=["GET", "POST"])
def render_plot():

    args = request.args
    palette = getitem(args, "color", "Accent")
    height = getitem(args, "plot_height", 600)
    width = getitem(args, "plot_width", 600)

    df = pd.DataFrame(np.random.randn(10, 4), columns=["x1", "x2", "y1", "y2"])

    script, div, js_resources, css_resources = graphs.plot_scatter(df[["x1", "x2"]], df[["y1", "y2"]], palette=palette,
                                                                   plot_height=int(height), plot_width=int(width))

    html = render_template("plot.html", options_list=list_palettes(), plot_script=script, plot_div=div["p"],
                           dot_slider=div["dot_size_slider"],
                           js_resources=js_resources, css_resources=css_resources, _from=10, _to=0, color=palette,
                           plot_height=height, plot_width=width)

    return encode_utf8(html)


def main():

    app.debug = True
    app.run()

if __name__ == '__main__':

    main()
