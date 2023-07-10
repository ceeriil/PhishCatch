from flask import Flask
from main import *
from app import *

app = Flask(__name__)

# Routes from app.py
@app.route('/')
def home():
	return render_template('home.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        vect = cv.transform(data).toarray()
        my_prediction = classifier.predict(vect)
        return render_template('result.html', prediction=my_prediction)
    
# Routes from main.py
@app.route('/url-detector')
def url():
    update_stats('visits')
    return render_template("index.html")

@app.route('/check', methods=['GET', 'POST'])
def check():
    update_stats('visits')
    if request.method == "POST":
        target_url = request.json['target']
        result = get_phishing_result(target_url=target_url)
        return jsonify(result)
    target_url = request.args.get("target")
    return render_template('check.html', target=target_url)

@app.route("/listen")
def listen():
    def respond_to_client():
        while True:
            stats = get_stats()
            _data = json.dumps(
                {"visits": stats['visits'], "checked": stats['checked'], "phished": stats['phished']})
            yield f"id: 1\ndata: {_data}\nevent: stats\n\n"
            time.sleep(0.5)
    
    return Response(respond_to_client(), mimetype='text/event-stream')

@app.route("/screenshot")
def screenshot():
    query = request.args
    if query and query.get("target"):
        target_url = query.get("target")
        today_date = date.today()

        width = default_screenshot_width
        height = default_screenshot_height

        if query.get("width") and query.get("height"):
            width = int(query.get("width"))
            height = int(query.get("height"))

        ss_file_name = secure_filename(f"{target_url}-{today_date}-{width}x{height}.png")
        ss_file_path = os.path.join(screenshot_dir, ss_file_name)

        if os.path.exists(ss_file_path):
            return send_from_directory(screenshot_dir, path=ss_file_name)

        return capture_screenshot(target_url=target_url, filename=ss_file_name, size=(width, height))
    abort(404)



if __name__ == '__main__':
    app.run(debug=True)
