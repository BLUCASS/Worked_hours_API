from flask import Flask, render_template, make_response, jsonify, request
from controller import DbManagement, Week

app = Flask(__name__)

@app.route('/home', methods=['GET'])
def home():
    """This is the homepage"""
    return render_template("home.html")

@app.route('/insert', methods=['GET'])
def database():
    """This is the form template"""
    return render_template("insert.html")

@app.route('/database', methods=['POST'])
def insert():
    """This page only shows that you succeeded"""
    data = request.form
    Week().get_week(data)
    return render_template("week_sent.html")

@app.route('/get_data', methods=['GET'])
def get_data():
    """This page will get the range data for the database"""
    return render_template("get_data.html")

@app.route('/view', methods=['POST'])
def view():
    """This page will show the database itself"""
    data = request.form
    data = DbManagement().view(data)
    if data == 404: return render_template("error.html")
    return render_template("view.html", list=data)

if __name__ == '__main__':
    app.run(debug=True)