import requests
import time
import json
import os
import Chatgpt
import access_token

from datetime import datetime
from bs4 import BeautifulSoup


startup_timestamp = time.time()

CONTENT_TYPE = "application/json"

def get_headers(bearer_token):
    """This is the headers for the Microsoft Graph API calls"""
    return {
        "Accept": CONTENT_TYPE,
        "Authorization": f"Bearer {bearer_token}",
        "ConsistencyLevel": "eventual",
    }

# 从token文件目录里面获取token的值
def file_get_bearer():
# 检查文件是否存在
	print("[+] Checking access token...")
	if os.path.exists('token/access_token.json'):
		with open('token/access_token.json') as f:
			token = json.load(f)
	else:
		print("[+] File does not exist, please generate the token again")
		access_token.get_access_token()
		with open('token/access_token.json') as f:
			token = json.load(f)
	print("[+] Token status: True")
	return token["access_token"]

# Check token
def check_token():
	user_bearer = file_get_bearer()
	url = "https://graph.microsoft.com/v1.0/me/chats"
	resp = requests.get(url, headers=get_headers(user_bearer))
	json_resp = resp.json()
	if "error" in json_resp:
		print("[+] Invalid Authentication Token, Token is expire")
		print("[+] Generating a new Microsoft Graph API token")
		access_token.refresh_token()
		user_bearer = file_get_bearer()
		print("[+] Connetion Microsoft Teams API Successful!")
		return user_bearer
	print("[+] Token is vaild!")
	print("[+] Connetion Microsoft Teams API Successful!")
	return user_bearer

def get_ms_teams_users(bearer_token):
    url = "https://graph.microsoft.com/v1.0/me"
    resp = requests.get(url, headers=get_headers(bearer_token))
    if resp.status_code != 200:
        print("[+] ERROR!",resp.json())
        return None

    json_resp = resp.json()
    try:
        return json_resp
    except KeyError as err:
        return []

def get_chat_id(bearer_token):
	url = "https://graph.microsoft.com/v1.0/me/chats"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp = resp.json()
	return json_resp["value"]

def get_chat_members(bearer_token, chat_id):
	url = f"https://graph.microsoft.com/v1.0/me/chats/{chat_id}/members"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp = resp.json()
	return json_resp["value"]

def get_chat_message(bearer_token):
	url = "https://graph.microsoft.com/v1.0/me/chats?$expand=lastMessagePreview"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp = error_info(resp)
	return json_resp["value"]

def creat_chat(bearer_token):
	create_chat_url = "https://graph.microsoft.com/v1.0/chats"
	data = {
		"chatType": "oneOnOne",
		"members": [
				{
				"@odata.type": "#microsoft.graph.aadUserConversationMember",
				"roles": ["owner"],
				"user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user_ms_teams_id}')",
				},
				{
				"@odata.type": "#microsoft.graph.aadUserConversationMember",
				"roles": ["owner"],
				"user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{sender_ms_team_id}')",
				},
			],
		}

	resp = requests.post(
		creat_chat_url, headers=get_headers(bearer_token), json=data)
	json_resp = resp.json()
	if resp.status_code not in [200, 201]:
		return False

def send_chat_message(bearer_token ,chat_id, message):
	chat_id = chat_id
	message = Chatgpt.send_chatgpt_message(message)
	send_message_url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
	messsage_data = {"body": {"contentType": "html", "content": message}}
	resp = requests.post(send_message_url, headers=get_headers(
		bearer_token), json=messsage_data)
	json_resp = resp.json()
	if resp.status_code not in [200, 201]:
		return False
	return True

def main(startup_timestamp):

        # First Check if the token is valid
	user_bearer = check_token()

	# Get SignedIn user data
	#users_data = get_ms_teams_users(user_bearer)

 	# Get SingnedIn user chat info
	#chat_id =  get_chat_id(user_bearer)

	# Get chatMessage in a channel or chat
	print("[+] Start listening last preview message")
	while True:
		user_bearer = check_token()
		chat_message = get_chat_message(user_bearer)

	# List chats along with the preview of the last message sent in the chat
		for item in chat_message:
                	topic = item["topic"]
                	chatType = item["chatType"]
                	content = item["lastMessagePreview"]["body"]["content"]
                	user = item["lastMessagePreview"]["from"]["user"]
                	createdDateTime = item["lastMessagePreview"]["createdDateTime"]
                	chat_id = item["id"]
                	if user is not None and chatType == "oneOnOne":
                        	dt = datetime.fromisoformat(createdDateTime)
                        	timestamp = dt.timestamp()
                        	if timestamp > startup_timestamp:
                        		displayName = item["lastMessagePreview"]["from"]["user"]["displayName"]
                        		if displayName != "Ziang Yu":
                        			print("[+] Chat id: " ,chat_id)
                        			print("[+] Displayname: " ,displayName)
                        			print("[+] chatType: " ,chatType)
                        			# Recevie new message
                        			message = get_content(content)
                        			print("[+] Content: ", message)
                        			print("[+] createdDateTime: " ,createdDateTime)
						# Auto Send message
                        			send_chat_message(user_bearer ,chat_id ,message)
                        			startup_timestamp = timestamp
                        			break
	time.sleep(5)

def auto_send_messages(startup_timestamp):
	# First Check if the token is valid
	user_bearer = check_token()

	# Get chatMessage in a channel or chat
	print("[+] Start listening new message")

	# Start loop, sleep time is 5
	while True:
		# Get new messages json
		try:
			chat_message = get_chat_message(user_bearer)
		except KeyError:
			print("[+] Connetion Microsoft Teams API failed")
			print("[+] Warning token is Expired!")
			user_bearer = check_token()
			chat_message = get_chat_message(user_bearer)
			print("[+] Start new listening progress")
		# Analyze json data
		for item in chat_message:
			chatType = item["chatType"]
			content = item["lastMessagePreview"]["body"]["content"]
			user = item["lastMessagePreview"]["from"]["user"]
			createdDateTime = item["lastMessagePreview"]["createdDateTime"]
			chat_id = item["id"]
			if user is not None and chatType == "oneOnOne":
				displayName = item["lastMessagePreview"]["from"]["user"]["displayName"]
				dt = datetime.fromisoformat(createdDateTime)
				timestamp = dt.timestamp()
				if timestamp > startup_timestamp and displayName != "Ziang Yu":
					print("[+] Chat id: " ,chat_id)
					print("[+] Displayname: " ,displayName)
					# Recevie new message
					message = get_content(content)
					print("[+] Content: ", message)
					# Recevie new time
					print("[+] createdDateTime: " ,createdDateTime)
					# Auto Send message
					# send_chat_message(user_bearer ,chat_id ,message)
					startup_timestamp = timestamp
					# End loop
					break
	time.sleep(5)

def get_content(content):
	html = content
	soup = BeautifulSoup(html, 'html.parser')
	ps = soup.find('p')
	message = ps.text
	return message

def all_chat_message():
	for item in chat_message:
		topic = item["topic"]
		chatType = item["chatType"]
		content = item["lastMessagePreview"]["body"]["content"]
		user = item["lastMessagePreview"]["from"]["user"]
		if user is not None:
			displayName = item["lastMessagePreview"]["from"]["user"]["displayName"]
			print("[+] Displayname: " ,displayName)
		else:
			print("[+] Displayname: None")
		print("[+] lastMessage: " ,content)

def chat():
	for item in chat_id:
		topic = item["topic"]
		id = item["id"]
		print("[+] Chat Name: ",item["topic"])
		print("[+] Chat ID: ",item["id"])
		chat_members = get_chat_members(user_bearer, id)
		for name in chat_members:
			print("[+] DisplayName", name["displayName"])
		print()

def get_group_members(bearer_token, chat_id):
        chat_id = chat_id
        url = f"https://graph.microsoft.com/v1.0/me/chats/{chat_id}/members"
        resp = requests.get(url, headers=get_headers(bearer_token))
        json_resp = resp.json()
        if resp.status_code not in [200, 201]:
                return False
        return json_resp

def display_members_name(bearer_token, chat_id):
	chat_id = "19:39b61a79436e4ace9f0c01259089e530@thread.v2"
	members = get_group_members(user_bearer, chat_id)
	for item in members["value"]:
		displayName = item["displayName"]
		email = item["email"]
		print(displayName)

# Search users by Email addrss
def search_user_id(bearer_token):
	while True:
		mail = input("[+] Input search email address: ")
		url = f"https://graph.microsoft.com/v1.0/users?$filter=userPrincipalName eq '{mail}'"
		resp = requests.get(url, headers=get_headers(bearer_token))
		json_resp = error_info(resp)
		if len(json_resp["value"]) != 0:
			displayName = json_resp["value"][0]["displayName"]
			user_id = json_resp["value"][0]["id"]
			print("[+] Find username: ", displayName)
			print("[+] User ID: ", user_id)
			break
		else:
			print("[+] User is not find!")
	return user_id

# Reset password and generate temporary password by search user ID
def change_password(bearer_token, user_id):
	password_auth = password_auth_methods(bearer_token, user_id)
	auth_method_id = password_auth["value"][0]["id"]
	url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/methods/{auth_method_id}/resetPassword"
	#data = {
	#	"lifetimeInMinutes": "60",
	#	"isUsableOnce": "true"
	#	}
	resp = requests.post(url, headers=get_headers(bearer_token))
	json_resp = error_info(resp)
	return json_resp

# User password settin by 3 method progress
def user_password_setting():
	user_bearer = check_token()
	user_id = search_user_id(user_bearer)
	if input("[+] Warning password password will be reset. Continue Y/N? ") != "N":
		json_resp = change_password(user_bearer, user_id)
		print("[+] Password reset success!")
		print("[+] Temporary access new password: ", json_resp["newPassword"])
		#print("[+] Life time in Minutes: ", json_resp["lifetimeInMinutes"])
	if input("[+] Do you want delete microsoft Authentication Method Y/N? ") !=  "N":
		delete_micro_auth_methods(user_bearer, user_id)

# Get password authentication methods id
def password_auth_methods(bearer_token, user_id):
	url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/passwordMethods"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp =  error_info(resp)
	return json_resp

# Get microsoft authenticator methods id
def micro_auth_methods(bearer_token, user_id):
	url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/microsoftAuthenticatorMethods"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp =  error_info(resp)
	return json_resp["value"]

# Get device info and microsoft Authenticator Methods id by user id
def device_micro_auth_methods(bearer_token, user_id):
	url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/microsoftAuthenticatorMethods"
	resp = requests.get(url, headers=get_headers(bearer_token))
	json_resp =  error_info(resp)
	auth_methods = json_resp["value"]
	if auth_methods and len(auth_methods) > 0:
		print("[+] Find microsoft Authenticator Methods!")
		for item in auth_methods:
			id = item['id']
			display_name = item['displayName']
			device_tag = item['deviceTag']
			print("[+] ID: ", id)
			print("[+] Display name: ", display_name)
			print("[+] Device tag: ", device_tag)
		return auth_methods
	else:
		return False

# Delete all microsoft verification methods
def delete_micro_auth_methods(bearer_token, user_id):
	auth_methods = device_micro_auth_methods(bearer_token, user_id)
	if auth_methods != False:
		for item in auth_methods:
			microsoftAuthenticatorMethods_id = item['id']
			url = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/microsoftAuthenticatorMethods/{microsoftAuthenticatorMethods_id}"
			resp = requests.delete(url, headers=get_headers(bearer_token))
			print("[+] Status code: ", resp.status_code)
		if resp.status_code == 204:
			print("[+] Delete microsoft Authenticator Methods success")
		else:
			print("[+] Delete microsoft Authenticator Methods faild")
	else:
		print("[+] No found microsoft Authenticator Methods!")

# Show error messages
def error_info(resp):
        json_resp = resp.json()
        if resp.status_code != 200 and "error" in json_resp:
                print("[+] Error code: ", json_resp["error"]["code"])
                print("[+] Error description: ", json_resp["error"]["message"])
                exit()
        else:
                return json_resp

if __name__ == "__main__":
#	auto_send_messages(startup_timestamp)
	user_password_setting()
#	chat_id = ""
#	display_members_name(bearer,chat_id)
#	search_user_id(bearer)
