import re
import base64
import requests
import time
import json
import os
import Chatgpt
import access_token
import asyncio
import microsoft_graph_api

from datetime import datetime
from bs4 import BeautifulSoup

def get_headers(bearer_token):
		CONTENT_TYPE = "application/json"
		return {
			"Accept": CONTENT_TYPE,
			"Authorization": f"Bearer {bearer_token}",
			"ConsistencyLevel": "eventual",
		}


def file_get_bearer():
		print("[+] Checking access token...")
		if os.path.exists('token/access_token.json'):
			with open('token/access_token.json') as f:
				token = json.load(f)
		else:
			print("[-] File does not exist, please generate the token again")
			paimon_bot_api.json_to_str(json_resp["mail"])
			access_token.get_access_token()
			with open('token/access_token.json') as f:
				token = json.load(f)
		print("[+] Token status: True")
		return token["access_token"]

def check_token():
		user_bearer = file_get_bearer()
		url = "https://graph.microsoft.com/v1.0/me/chats"
		resp = requests.get(url, headers=get_headers(user_bearer))
		json_resp = resp.json()
		if "error" in json_resp:
			print("[-] Invalid Authentication Token, Token is expire")
			print("[+] Generating a new Microsoft Graph API token")
			access_token.refresh_token()
			user_bearer = file_get_bearer()
			print("[+] Connetion Microsoft Teams API Successful!")
			return user_bearer
		print("[+] Token is vaild!")
		print("[+] Connetion Microsoft Teams API Successful!")
		return user_bearer

# Search users by Email addrss
def search_user_id(bearer_token, name):
		name = re.sub(r'<[^<]+?>', '', name)
		if "@mdpi" in name:
			name = name.split("@")[0]
			name = name.replace(".", " ")
		print("[+] Search display name:", name)
		url = f"https://graph.microsoft.com/v1.0/users?$filter=displayName eq '{name}'"
		resp = requests.get(url, headers=get_headers(bearer_token))
		json_resp = error_info(resp)
		if len(json_resp["value"]) != 0:
			displayName = json_resp["value"][0]["displayName"]
			user_id = json_resp["value"][0]["id"]
			print("[+] Find username: ", displayName)
			print("[+] User ID: ", user_id)
			return json_resp
		else:
			print("[-] User is not find!")
			return None

def change_password(name):
	bearer_token = check_token()
	user = search_user_id(bearer_token, name)
	if user == None:
		return None, None
	user_name = user["value"][0]["displayName"]
	user_id = user["value"][0]["id"]
	password_auth = microsoft_graph_api.password_auth_methods(bearer_token, user_id)
	auth_method_id = password_auth["value"][0]["id"]
	url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/methods/{auth_method_id}/resetPassword"
	resp = requests.post(url, headers=get_headers(bearer_token))
	json_resp = error_info(resp)
	print("[+] Password reset success!")
	print("[+] Temporary access new password: ", json_resp["newPassword"])
	return json_resp, user_name

def user_profiles(name):
	bearer_token = check_token()
	user = search_user_id(bearer_token, name)
	if user == None:
		return None
	user_id = user["value"][0]["id"]
	url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp = error_info(resp)
	print("[+] Display Name: ", json_resp["displayName"])
	print("[+] login name: ", json_resp["userPrincipalName"])
	print("[+] Email Address: ", json_resp["mail"])
	print("[+] Office Location: ", json_resp["officeLocation"])
	return json_resp

def user_devices(name):
	bearer_token = check_token()
	user = search_user_id(bearer_token, name)
	if user == None:
		return None
	user_id = user["value"][0]["id"]
	user_devices_id = devices_id(bearer_token, user_id)
	if user_devices_id:
		print("[+] Find user devices!")
		for item in user_devices_id:
			print("[+] Device name: ", item["displayName"])
			print("[+] OS: ", item["operatingSystem"])
		return user_devices_id

def user_recoverykeys(user_device_id):
	bearer_token = check_token()
	recovery_keys_id = recoverykeys_id(bearer_token, user_device_id)
	return recovery_keys_id, bearer_token

# Get deviceId by search user email or name
def devices_id(bearer_token, user_id):
	url = f'https://graph.microsoft.com/v1.0/users/{user_id}/registeredDevices'
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp =  error_info(resp)
	return json_resp["value"]

# Get user information Protection bitlocker Keys by recoveryKeys id
def recovery_key(bearer_token, bitlockerRecoveryKey_id):
        url = f"https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys/{bitlockerRecoveryKey_id}/?$select=key"
        resp = requests.get(url, headers=get_headers(bearer_token))
        json_resp =  error_info(resp)
        return json_resp["key"]

# Get user information Protection bitlocker recoveryKeys id by device id
def recoverykeys_id(bearer_token, user_device_id):
        url = f"https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys?$filter=deviceId eq '{user_device_id}'"
        resp = requests.get(url, headers=get_headers(bearer_token))
        json_resp =  error_info(resp)
        return json_resp

# Show volume type information
def volume_type(type):
	if type == "1":
		print("[+] Volume type: Operating System Volume")
		type = "操作系统驱动器"
		return type
	elif type == "2":
		print("[+] Volume type: Fixed Data Volume")
		type = "数据驱动器"
		return type
	elif type == "3":
		print("[+] Volume type: Removable Data Volume")
		type = "移动硬盘驱动器"
		return type
	else:
		print("[+] Volume type: Unknown Future Value")
		type = "未知硬盘驱动器"
		return type

# Show error messages
def error_info(resp):
	json_resp = resp.json()
	if resp.status_code != 200 and "error" in json_resp:
		print("[-] Error code: ", json_resp["error"]["code"])
		print("[-] Error description: ", json_resp["error"]["message"])
		return False
	else:
		return json_resp

# json data to string
def json_to_str(json_resp):
	if json_resp is None:
		return ""
	json_str = json.dumps(json_resp)
	json_str_no_quotes = json_str.replace('"', '')
	return json_str_no_quotes

def image_send(image_path):
	image_name = os.path.basename(image_path)
	image_attachment = Attachment(
		content_url=f"file://{image_path}",
		content_type="image/png",
		name=f"{image_name}"
	)
	return image_attachment
