# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json
import Chatgpt
import paimon_bot_api

from typing import List
from botbuilder.core import CardFactory, TurnContext, MessageFactory
from botbuilder.core.teams import TeamsActivityHandler, TeamsInfo
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters, Attachment, Activity, CardImage
from botbuilder.schema.teams import TeamInfo, TeamsChannelAccount
from botbuilder.schema._connector_client_enums import ActionTypes

ADAPTIVECARDTEMPLATE = "resources/UserMentionCardTemplate.json"

class TeamsConversationBot(TeamsActivityHandler):
	def __init__(self, app_id: str, app_password: str):
		self._app_id = app_id
		self._app_password = app_password

	async def on_message_activity(self, turn_context: TurnContext):
		TurnContext.remove_recipient_mention(turn_context.activity)
		text = turn_context.activity.text.strip().lower()
		print("[+] Content message: ", text)
		if "@paimon" in text:
			await self._chatgpt(turn_context, text)
			return
		if "hi" in text or "你好" in text:
			await self._paimon_activity(turn_context)
			return
		if "搜索" in text:
			await self._user_profiles(turn_context, text)
			return
		if "ai" in text or "chatgpt" in text:
			await self._chatgpt_info(turn_context, text)
			return
		if "重置密码" in text:
			await self._password_reset(turn_context, text)
			return
		if "wifi" in text:
			await self._wifi_card(turn_context)
			return
		print("[+] Warn: No found keyword")

	async def _paimon_activity(self, turn_context: TurnContext):
		print("Welcome")
		mention = Mention(
			mentioned=turn_context.activity.from_property,
			text=f"<at>{turn_context.activity.from_property.name}</at>",
		)
		#reply_activity = MessageFactory.text(f"Hello {mention.text}")
		reply_activity = MessageFactory.text("你好啊旅行者,我是派蒙!")
		reply_activity.entities = [Mention().deserialize(mention.serialize())]
		await turn_context.send_activity(reply_activity)

	async def _user_profiles(self, turn_context: TurnContext, message):
		reply_activity = MessageFactory.text("正在为旅行者搜索用户中！请稍等片刻...")
		await turn_context.send_activity(reply_activity)
		search_name = message[message.index("搜索") + 2:]
		json_resp = paimon_bot_api.user_profiles(search_name)
		if json_resp is not None:
			reply_activity = MessageFactory.text("派蒙已经成功搜索到！")
			await turn_context.send_activity(reply_activity)
			displayName = paimon_bot_api.json_to_str(json_resp["displayName"])
			user_id = json_resp["id"]
			officeLocation = paimon_bot_api.json_to_str(json_resp["officeLocation"])
			mail = paimon_bot_api.json_to_str(json_resp["mail"])
			reply = "旅行者姓名: " + displayName + "\n" + "旅行者uid: "  + user_id + "\n" + "旅行者地点: " + officeLocation + "\n" + " 旅行者邮箱: " + mail
			reply_activity = MessageFactory.text(reply)
			await turn_context.send_activity(reply_activity)
		elif json_resp is False:
			reply_activity = MessageFactory.text("对不起哦旅行者,服务器发生错误,请联系IT")
			await turn_context.send_activity(reply_activity)
		else:
			reply_activity = MessageFactory.text("对不起哦旅行者,冒险世界里面没有这个人,请重新搜索")
			await turn_context.send_activity(reply_activity)

	async def _chatgpt_info(self, turn_context: TurnContext, message):
		reply_activity = MessageFactory.text("派蒙正在接入ChatGpt中！请稍等片刻...")
		await turn_context.send_activity(reply_activity)
		reply_activity = MessageFactory.text("ChatGpt接入成功！请使用@paimon对我进行对话...")
		await turn_context.send_activity(reply_activity)

	async def _chatgpt(self, turn_context: TurnContext, message):
		message = message[message.index("@paimon") + 2:]
		reply = Chatgpt.send_chatgpt_message(message)
		reply_activity = MessageFactory.text(reply)
		await turn_context.send_activity(reply_activity)

	async def _password_reset(self, turn_context: TurnContext, message):
		reply_activity = MessageFactory.text("正在为旅行者重置密码中！请稍等片刻...")
		await turn_context.send_activity(reply_activity)
		user = message[message.index("重置密码") + 4:]
		json_resp, user_name = paimon_bot_api.change_password(user)
		if json_resp is not None:
			tmpassword = json_resp["newPassword"]
			reply = "派蒙已成功为您重置密码!\n" + "用户名: " + user_name + "\n" + "临时密码: " + tmpassword + "\n"
			reply_activity = MessageFactory.text(reply)
			await turn_context.send_activity(reply_activity)
		else:
			reply_activity = MessageFactory.text("对不起哦旅行者,冒险世界里面没有这个人,重置密码失败！")
			await turn_context.send_activity(reply_activity)

	async def _wifi_card(self, turn_context: TurnContext):
		reply_activity = MessageFactory.text("尊敬的旅行者,WiFi密码为wuhan2013")
		await turn_context.send_activity(reply_activity)
		image_path = 'resources/WiFi_Card.png'
		with open(image_path, "rb") as image_file:
			image_data = image_file.read()
		image_name = os.path.basename(image_path)
		image_attachment = Attachment(
			name=image_name,
			content_type="image/png",
			content_url=f"data:image/png;base64,{image_data.decode('ISO-8859-1')}"
		)
		#attachment = paimon_bot_api.image_send(path)
		reply_activity = MessageFactory.attachment(image_attachment)
		await turn_context.send_activity(reply_activity)
