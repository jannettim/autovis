# -*- coding: utf-8 -*-
"""
Created on Wed May 03 11:26:21 2017

@author: Kevin Anderson

https://github.com/bokeh/bokeh/issues/6096
"""

import pandas as pd
from bokeh.models import ColumnDataSource, CustomJS, DataTable, TableColumn
from bokeh.layouts import row

import io
import base64

import graphs


class ImportData:

    def __init__(self):

        self.file_source = ColumnDataSource({'file_contents': [], 'file_name': []})

        self.df = None

        self.layout = None
        self.doc = None
        self.x_drop = None
        self.y_drop = None
        self.g_drop = None
        self.dt = None
        self.submit = None

        self.g_label = None
        self.x_label = None
        self.y_label = None

        self.plot_type = None
        self.plot_label = None

        self.cb = CustomJS(args=dict(file_source=self.file_source), code="""
            function read_file(filename) {
                var reader = new FileReader();
                reader.onload = load_handler;
                reader.onerror = error_handler;
                // readAsDataURL represents the file's data as a base64 encoded string
                reader.readAsDataURL(filename);
            }

            function load_handler(event) {
                var b64string = event.target.result;
                file_source.data = {'file_contents' : [b64string], 'file_name':[input.files[0].name]};
                file_source.trigger("change");
            }

            function error_handler(evt) {
                if(evt.target.error.name == "NotReadableError") {
                    alert("Can't read file!");
                }
            }

            var input = document.createElement('input');
            input.setAttribute('type', 'file');
            input.onchange = function(){
                if (window.FileReader) {
                    read_file(input.files[0]);
                } else {
                    alert('FileReader is not supported in this browser');
                }
            }
            input.click();
            """)

        self.file_source.on_change('data', self.file_callback)

    def select_cols_x(self, attr, old, new):

        self.x_drop.label = new

    def select_cols_y(self, attr, old, new):

        self.y_drop.label = new

    def select_cols_g(self, attr, old, new):

        self.g_drop.label = new

    def load_preview(self):
        source = ColumnDataSource(data=dict())
        columns = []

        for col in self.df.columns:
            source.data.update({col: self.df.head(10)[col].tolist()})
            columns.append(TableColumn(field=col, title=col))

        self.dt.source = source
        self.dt.columns = columns
        self.x_drop.menu = [("None", None)] + list(zip(self.df.columns.tolist(), self.df.columns.tolist()))
        self.y_drop.menu = [("None", None)] + list(zip(self.df.columns.tolist(), self.df.columns.tolist()))
        self.g_drop.menu = [("None", None)] + list(zip(self.df.columns.tolist(), self.df.columns.tolist()))
        self.doc.add_root(row([self.dt]))
        self.doc.add_root(row([self.x_label, self.y_label, self.g_label]))
        self.doc.add_root(row([self.x_drop, self.y_drop, self.g_drop]))
        self.doc.add_root(row([self.plot_label]))
        self.doc.add_root(row([self.plot_type]))
        self.doc.add_root(row([self.submit]))

        self.x_drop.on_change("value", self.select_cols_x)
        self.y_drop.on_change("value", self.select_cols_y)
        self.g_drop.on_change("value", self.select_cols_g)
        self.submit.on_click(self.submit_callback)

    def file_callback(self, attr, old, new):

        raw_contents = self.file_source.data['file_contents'][0]
        # remove the prefix that JS adds
        prefix, b64_contents = raw_contents.split(",", 1)

        file_contents = base64.b64decode(b64_contents)
        file_io = io.StringIO(file_contents.decode("latin-1"))

        self.df = pd.read_csv(file_io)

        self.load_preview()

    def submit_callback(self):

        x = self.x_drop.value
        y = self.y_drop.value
        group = self.g_drop.value

        plot_type = self.plot_type.labels[self.plot_type.active]

        if group is None:
            gp = graphs.GraphPlot(x=self.df[x], y=self.df[y])
        else:
            gp = graphs.GraphPlot(x=self.df[x], y=self.df[y], group=self.df[group])

        if plot_type == "Scatter":

            app_layout = gp.plot_scatter()

        elif plot_type == "Line":

            app_layout = gp.plot_line()

        elif plot_type == "Bar":

            app_layout = gp.plot_bar()

        elif plot_type == "Histogram":

            app_layout = gp.plot_histogram(7)

        else:

            app_layout = None

        self.doc.clear()

        self.doc.add_root(app_layout)

