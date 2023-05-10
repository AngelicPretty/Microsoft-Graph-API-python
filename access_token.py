import requests
import json
import os
import configparser

config = configparser.ConfigParser()
config.read(['config.ini'])

azure = config['azure']
url = config['url']
response = config['response']
scope = config['scope']

client_id = azure['client_id']
tenant_id = azure['tenant_id']
client_secret = azure['client_secret']
redirect_uri = url['redirect_uri']


#client_id = "40af39aa-a901-4b50-b5e5-be6e8b2d45a8"
#client_secret = "~rS8Q~IK3h3u-Eh3WH1v5Fncx6CtxP~jl_y2Hc8l"
#tenant_id = "a17f8ab9-bc70-4901-a8ac-c4b71563637c"

#redirect_uri = "https://188.188.13.121:5000"

def file_get_code():
# Check file exits
	print("[+] Checking code...")
	if os.path.exists('token/code.json'):
		with open('token/code.json') as f:
			code = json.load(f)
	else:
		print("[-] File does not exist, please generate the code")
		exit()

	if "code" in code:
		print("[+] Token exist: true")
		return code["code"][0]
	else:
		print("[+] Get code failed")
		print("[+] Please generate the code")
		exit()

def file_get_refresh_code():
# Check file exits
	print("[+] Checking refresh code...")
	if os.path.exists('token/access_token.json'):
		with open('token/access_token.json') as f:
			access_token = json.load(f)
	else:
		print("[-] File does not exist, Start generate the access token")
		get_access_token()
		with open('token/access_token.json') as f:
			access_token = json.load(f)
	if "refresh_token" in access_token:
		print("[+] Refresh token exist: true")
		return access_token["refresh_token"]
	else:
		print("[+] Get refresh token failed")
		exit()

# Get code generate access token
def get_access_token():
	grant_type = "authorization_code"
	code = file_get_code()
	url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
	payload = (
		f"client_id={client_id}&client_secret={client_secret}"
		f"&grant_type={grant_type}&redirect_uri={redirect_uri}"
		f"&code={code}"
		)
	headers = {}
	resp = requests.request("POST", url, headers=headers,data=payload)
	json_resp = error_info(resp)
	print("[+] Token type :" ,json_resp["token_type"])
	print("[+] Scope :", json_resp["scope"])
	print("[+] Get the new access token")
	access_token = resp.json()
	with open("token/access_token.json","w") as f:
		json.dump(access_token, f)
	print("[+] Save access token to local file Success")

# Refresh the access token
def refresh_token():
	grant_type = "refresh_token"
	refresh_token = file_get_refresh_code()
	url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
	headers = {}
	payload = (
			f"client_id={client_id}&client_secret={client_secret}"
			f"&grant_type={grant_type}&redirect_uri={redirect_uri}"
			f"&refresh_token={refresh_token}"
			)
	resp = requests.request("POST", url, headers=headers,data=payload)
	json_resp = error_info(resp)
	print("[+] Token type:" ,json_resp["token_type"])
	print("[+] Scope:", json_resp["scope"])
	print("[+] Refresh new access token!")
	access_token = resp.json()
	with open("token/access_token.json","w") as f:
		json.dump(access_token, f)
	print("[+] Update new access token to local file Success")

# Show error messages
def error_info(resp):
	json_resp = resp.json()
	if resp.status_code != 200 and "error" in json_resp:
		print("[-] Error :", json_resp["error"])
		print("[-] Error description :", json_resp["error_description"])
		exit()
	else:
		return json_resp

if __name__ == "__main__":

#	get_access_token(client_id, client_secret, tenant_id, redirect_uri)
	refresh_token()
