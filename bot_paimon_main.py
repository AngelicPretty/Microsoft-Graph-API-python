import sys
import traceback
import uuid
from datetime import datetime
from http import HTTPStatus

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from teams_conversion_paimon import TeamsConversationBot
from config import DefaultConfig

CONFIG = DefaultConfig()

SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


#ADAPTER.on_turn_error = on_error

APP_ID = SETTINGS.app_id if SETTINGS.app_id else uuid.uuid4()

# Create the Bot
BOT = TeamsConversationBot(CONFIG.APP_ID, CONFIG.APP_PASSWORD)

# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    # Main bot message handler.
	if "application/json" in req.headers["Content-Type"]:
		body = await req.json()
	else:
		return Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
	activity = Activity().deserialize(body)
	auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

	# message info
	print("[+] Channel type: ", body["channelId"])

	response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
	if response:
		return json_response(data=response.body, status=response.status)
	return Response(status=HTTPStatus.OK)

APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
	try:
		web.run_app(APP, host="localhost", port=CONFIG.PORT)
	except Exception as error:
		raise error
