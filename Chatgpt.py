
import os
import requests
import json
import openai

os.environ["HTTP_PROXY"] = "127.0.0.1:1089"
os.environ["HTTPS_PROXY"] = "127.0.0.1:8889"
# 设置OpenAI API密钥和端点URL
openai.api_key = '{api-key}'
openai_endpoint = 'https://api.openai.com/v1/engines/text-davinci-003/completions'
model_engine = "text-davinci-003"
messages = []
openai.organization = os.environ.get("ORG_ID")

# 定义用于向API发送请求并获取响应的函数
def chat_gpt(prompt):
	try:
		response = openai.Completion.create(
			engine=model_engine,
			prompt=prompt,
			max_tokens=1024,
			n=1,
			stop=None,
			temperature=0.7,
		)
	except openai.error.RateLimitError as e:
		print("[-] Warning: Your api key is expired!")
		message = "您的Open API的密钥已经过期,请重新获取！"
		return message
	print("[+] Send Status: 200")
	message = response.choices[0].text.strip()
	return message

def __init__(messages=[]) -> None:
        # 初始化对话列表，可以加入一个key为system的字典，有助于形成更加个性化的回答
        # self.conversation_list = [{'role':'system','content':'你是一个非常友善的助手'}]
        messages = []

# 接受并发送消息
def send_chatgpt_message(message):
	user_input = message
	if user_input == 'bye':
		print("[+] Send Status: 200")
		response = "再见"
		return response
	else:
		answer_name = "PaimonAI"
		prompt = f"Q: {user_input}\n{answer_name}: "
		response = chat_gpt(prompt)
		return response
