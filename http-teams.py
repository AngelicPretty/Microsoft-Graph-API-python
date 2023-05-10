from flask import Flask, render_template, request, redirect ,url_for, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
import microsoft_graph_api
import time

app = Flask(__name__)

# Scheduled token rrefresh every 1 hours
def refresh_token():
	microsoft_graph_api.check_token()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
	email = request.form['text']
	print(f"[+] URL 参数值：{email}")
	resp = microsoft_graph_api.add_member(email)
	if resp == True:
		status = "Join teams group Success!"
	else:
		status = "Join teams group Failed!"
	return redirect(url_for('result', status=status))

@app.route('/result/<status>')
def result(status):
	return render_template('result.html', status=status)

# image server build
IMAGE_FOLDER = "/home/misakimei/CTOS/Microsoft-API/resources"
@app.route('/image/<path:filename>')
def send_image(filename):
	return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
	scheduler = BackgroundScheduler()
	job = scheduler.add_job(refresh_token, 'interval', hours=2)
	scheduler.start()
	app.run(host='localhost', port=5000)
