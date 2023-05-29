import requests
import json
import os
import datetime
import requests
from tabulate import tabulate
from bs4 import BeautifulSoup

#设置代理
os.environ["HTTP_PROXY"] = "127.0.0.1:1089"
os.environ["HTTPS_PROXY"] = "127.0.0.1:8889"

def main():
	print('')

	choice = -1
	while choice != 0:
		os.system('cls' if os.name == 'nt' else 'clear')
		print("")
		print('Little Fish ChataGPT key Tools v1.0')
		print('Copyright (C) Little Fish. All rights reserved.')
		print("______________________________________________________________")
		print('')
		print('[1] Local keys ')
		print('[2] Online keys')
		print("")
		print("——————————————————————————————————————————————————————————————")
		print('[9] Read Me')
		print("[0] Exit")
		print("")
		print("——————————————————————————————————————————————————————————————")
		print("")
		try:
			choice = int(input("Enter a menu option in the Keyboard [0,1,2,9]: "))
		except ValueError:
			choice = -1
		if choice == 0:
			print('[+] Goodbye...')
		elif choice == 1:
			local_keys()
		elif choice == 2:
			online_keys()
		else:
			print('[-] Invalid choice!\n')

def local_keys():
	os.system('cls' if os.name == 'nt' else 'clear')
	apikey_list = get_local_apikey()
	api_key_check(apikey_list)
	print("[+] Press Enter key to continue")
	input()

def online_keys():
	os.system('cls' if os.name == 'nt' else 'clear')
	apikey_list = get_apikey()
	api_key_check(apikey_list)
	print("[+] Press Enter key to continue")
	input()

#从本地文件获取api-keys
def get_local_apikey():
	with open('./resources/chatgpt-apikey.txt', 'r') as file:
		api_list = file.read()
		api_list = api_list.split('\n')
		api_list = [x.strip() for x in api_list if x.strip()]
		return api_list

#从网络在线获取api-keys
def get_apikey():
	url = "https://freeopenai.xyz/api.txt"
	response = requests.get(url).text
	response = response.split('\n')
	api_list = [x.strip() for x in response if x.strip()]
	return api_list

def check_billing(api_key):
	#格式化时间
	def formatDate(date):
		year = date.year
		month = str(date.month).zfill(2)
		day = str(date.day).zfill(2)
		return f"{year}-{month}-{day}"

	#计算起始日期和结束日期
	now = datetime.datetime.now()
	startDate = now - datetime.timedelta(days=90)
	endDate = now + datetime.timedelta(days=1)
	subDate = now.replace(day=1)

	#设置API请求URL和请求头

	#查是否订阅
	url_sub = "https://api.askgptai.tech/v1/dashboard/billing/subscription"
	#查普通账单
	url_balance = "https://api.askgptai.tech/dashboard/billing/credit_grants"
	#查询用量
	url_usage = "https://api.askgptai.tech//v1/dashboard/billing/usage?start_date={}&end_date={}".format(formatDate(startDate), formatDate(endDate))
	headers = {"Authorization": f"Bearer {api_key}"}

	response_sub = requests.get(url_sub, headers=headers)
	if response_sub.status_code == 200:
		data_sub = response_sub.json()
		total_amount = data_sub["hard_limit_usd"]

		if total_amount > 20:
			startDate = subDate

		#重新生成url_usage
		url_usage = "https://api.askgptai.tech//v1/dashboard/billing/usage?start_date={}&end_date={}".format(formatDate(startDate), formatDate(endDate))
		response_usage = requests.get(url_usage, headers=headers)
		if response_usage.status_code == 200:
			data_usage = response_usage.json()
			#获取已使用量
			total_usage = data_usage["total_usage"] / 100
			#计算剩余额度
			remaining = total_amount - total_usage
			#保存为json格式
			remaining = round(remaining, 2)
			total_usage = round(total_usage, 2)
			total_amount = round(total_amount, 2)
			api_usage_data = {"API-KEY":api_key, "status":response_sub.status_code,"TotalAmount": total_amount, "TotalUsage": total_usage,"Remaining":remaining}
			return api_usage_data
	else:
		print(f"[-] Search failed，status code: {response_sub.status_code}")
		api_usage_data = {"API-KEY":api_key, "status":response_sub.status_code,"TotalAmount": None, "TotalUsage": None,"Remaining":None}
		return api_usage_data

#API-key批量检查
def api_key_check(api_list):
	useable = 0
	api_usage_datas = []
	for api_key in api_list:
		print("[+] API key:", api_key)
		api_usage_data = check_billing(api_key)
		api_usage_datas.append(json.dumps(api_usage_data))
		if api_usage_data != None:
			useable += 1
			print("[+] Total amount: ",api_usage_data["TotalAmount"])
			print("[+] Total usage: ",api_usage_data["TotalUsage"])
			print("[+] Remaining: ",api_usage_data["Remaining"])
	print("[+] API total: ", len(api_list))
	print("[+] API Useable: ", useable)
	api_usage_datas = "[" + ",".join(api_usage_datas) + "]"
	data = json.loads(api_usage_datas)
	headers = list(data[0].keys())
	data_list = [list(item.values()) for item in data]
	table = tabulate(data_list, headers=headers, tablefmt="grid")
	print(table)

if __name__ == '__main__':
	main()
