from bokeh.models import ColumnDataSource, CustomJS, Button, DataTable, TableColumn, Dropdown
from bokeh.layouts import layout
from bokeh.plotting import curdoc

from file_input import ImportData

imp_data = ImportData()
button = Button(label="Upload")
button.js_on_click(imp_data.cb)

imp_data.x_drop = Dropdown(label="x column")
imp_data.y_drop = Dropdown(label="y column")
imp_data.g_drop = Dropdown(label="group column")
imp_data.dt = DataTable()

app_layout = layout([button])
doc = curdoc()

imp_data.layout = app_layout
imp_data.doc = doc

doc.add_root(app_layout)