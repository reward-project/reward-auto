from jinja2 import Environment, PackageLoader, select_autoescape#
from jinja2 import StrictUndefined #
from flask import Flask, render_template
app = Flask(__name__)
app.jinja_env.undefined = StrictUndefined#

@app.route("/")
def template_test():
    return render_template('template.html', my_string="Wheeeee!", my_list=[0,1,2,3,4,5])


if __name__ == '__main__':
    app.run(host='222.122.202.122', port=5000,debug = True)
 