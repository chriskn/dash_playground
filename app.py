import dash


app = dash.Dash(name="Sat", url_base_pathname="/sat/")
app.title = "Sat"
server = app.server
app.config.suppress_callback_exceptions = True
