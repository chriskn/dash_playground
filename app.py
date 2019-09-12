import dash
from flask_caching import Cache

app = dash.Dash(name="Sat", url_base_pathname="/sat/")
app.title = "Sat"
cache = Cache(
    app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": ".flask-cache"}
)
app.config.suppress_callback_exceptions = True
