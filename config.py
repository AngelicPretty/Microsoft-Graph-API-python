#!/usr/bin/env python3
# Copyright (c) LittleFish Corporation. All rights reserved.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 5050
    APP_ID = os.environ.get("MicrosoftAppId", "{Microsoft App id}")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "{Microsoft App Password}")
