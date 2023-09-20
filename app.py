from flask import Flask
from extensions import cache
from views import *


app = Flask(__name__)


# Initialize the cache
cache.init_app(app)

app.add_url_rule('/', view_func=home, methods=['GET'])
app.add_url_rule('/search', view_func=search, methods=['GET', 'POST'])
app.add_url_rule('/author/<author_id>/overview', view_func=author_overview, methods=['GET'])
app.add_url_rule('/author/<author_id>/overview_filtered', view_func=author_overview_filtered, methods=['POST'])
app.add_url_rule('/project/<project_id>', view_func=project, methods=['GET'])
app.add_url_rule('/share_profile/<author_id>', view_func=share_profile, methods=['GET'])


if __name__ =="__main__":     
    app.run(debug=True)
