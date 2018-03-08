from flask import render_template, Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def mainpage():
    return render_template('main.html')

@app.route('/search')
def search_result():
    keyword = request.args.get('keyword', ' ', type=str)
    print(keyword)
    return jsonify(result=1)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
