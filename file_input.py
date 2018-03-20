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

    def load_preview(self):
        source = ColumnDataSource(data=dict())
        columns = []

        for col in self.df.columns:
            source.data.update({col: self.df.head(10)[col].tolist()})
            columns.append(TableColumn(field=col, title=col))

        self.dt.source = source
        self.dt.columns = columns
        self.x_drop.menu = list(zip(self.df.columns.tolist(), self.df.columns.tolist()))
        self.y_drop.menu = list(zip(self.df.columns.tolist(), self.df.columns.tolist()))
        self.g_drop.menu = list(zip(self.df.columns.tolist(), self.df.columns.tolist()))
        self.doc.add_root(row([self.dt]))
        self.doc.add_root(row([self.x_drop, self.y_drop, self.g_drop]))

    def file_callback(self, attr, old, new):

        raw_contents = self.file_source.data['file_contents'][0]
        # remove the prefix that JS adds
        prefix, b64_contents = raw_contents.split(",", 1)

        file_contents = base64.b64decode(b64_contents)
        file_io = io.StringIO(file_contents.decode("latin-1"))

        self.df = pd.read_csv(file_io)

        self.load_preview()

        # return self.cb


