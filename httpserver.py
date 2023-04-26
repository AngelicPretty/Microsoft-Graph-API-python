from apscheduler.schedulers.background import BackgroundScheduler
import time
from flask import Flask, request
import microsoft_graph_api

app = Flask(__name__)

def refresh_token():
	microsoft_graph_api.check_token()

scheduler = BackgroundScheduler()
job = scheduler.add_job(refresh_token, 'interval', hours=2)
scheduler.start()

@app.route('/')
def index():
    # 获取 URL 参数
	param_value = request.args.get('mail', 'default_value')

    # 在这里处理参数值
	print(f"URL 参数值：{param_value}")
	status = microsoft_graph_api.add_member(param_value)
	if status == True:
		return "加入群聊小组成功"
	else:
		return "加入群聊小组失败"

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
