from flask import render_template, Flask, request, jsonify
from main import query

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mainpage():
    return render_template('main.html')

@app.route('/search')
def search_result():
    keyword = request.args.get('keyword', ' ', type=str)
    start = request.args.get('start', ' ', type=int)
    res = query(keyword, start, 10)
    print(res)
    return jsonify(res=res)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
