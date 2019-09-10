import dash

app = dash.Dash(name="Sat", url_base_pathname="/sat/")
server = app.server
app.config.suppress_callback_exceptions = True