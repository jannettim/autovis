from bokeh.models import Button, DataTable, Dropdown, PreText, RadioButtonGroup
from bokeh.layouts import layout
from bokeh.plotting import curdoc

from file_input import ImportData

imp_data = ImportData()
button = Button(label="Upload", button_type="success")
button.js_on_click(imp_data.cb)

imp_data.x_label = PreText(text="x axis variable")
imp_data.y_label = PreText(text="y axis variable")
imp_data.g_label = PreText(text="group variable")

imp_data.x_drop = Dropdown(label="x-axis Variable")
imp_data.y_drop = Dropdown(label="y-axis Variable")
imp_data.g_drop = Dropdown(label="Group Variable")
imp_data.dt = DataTable()
imp_data.plot_type = RadioButtonGroup(labels=["Line", "Bar", "Scatter", "Histogram"])
imp_data.plot_label = PreText(text="Plot type")
imp_data.submit = Button(label="Submit", button_type="success")

app_layout = layout([button])
doc = curdoc()

imp_data.layout = app_layout
imp_data.doc = doc

doc.add_root(app_layout)