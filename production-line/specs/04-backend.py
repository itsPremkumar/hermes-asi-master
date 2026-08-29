from flask import Flask, request, jsonify, redirect
app = Flask(__name__)
url_store = {}
@app.route('/api/shorten', methods=['POST'])
def shorten():
    data = request.get_json()
    if 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    short_code = str(len(url_store))
    url_store[short_code] = data['url']
    return jsonify({'short_code': short_code}), 201
@app.route('/<code>')
def get_url(code):
    url = url_store.get(code)
    if not url:
        return jsonify({'error': 'Not found'}), 404
    return redirect(url)
if __name__ == '__main__':
    app.run(debug=True)
