from flask import Flask, render_template, request, jsonify
from index import main_query

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = main_query(query)  
    return jsonify({"data" : results})

if __name__ == '__main__':
    app.run(debug=True)