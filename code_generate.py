import http.server
import socketserver
import urllib.parse
import json
import ssl
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
response_type = response['response_type']
scope = scope['scope']

url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}"

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 获取重定向的URL，并解析其中的参数
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        # 获取AccessToken，并输出到控制台
        if 'code' in params:
            #print('[+] code : ', params['code'][0])
            with open("token/code.json","w") as f:
                 json.dump(params, f)
                 print("[+] Save access_token to local file Success!")
                 exit()

        # 发送响应
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<html><head><title>OAuth2 Callback</title></head>")
        self.wfile.write(b"<body><h1>OAuth2 Callback Received!</h1></body></html>")

    def log_message(self, format: str, *args):
        return

# 启动Web服务器，并监听指定端口
PORT = 5050
certfile = 'token/cert.pem'
keyfile = 'token/key.pem'
context= ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=certfile, keyfile=keyfile)

with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
	print("[+] Https Server started at localhost:", PORT)
	print("[+] Microsoft Graph API Authorization")
	print("[+] Start generate new code")
	print("[+] Please open web browser input URL:")
	print("[+] Scopes: ", scope)
	print("[+] URL: ",url)
	httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
	httpd.serve_forever()
