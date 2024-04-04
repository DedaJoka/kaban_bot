import requests
from requests import RequestException
import traceback
from viberbot.api.consts import BOT_API_ENDPOINT
import json

import hashlib
import hmac
import json
import logging

import requests
from viberbot.api.consts import VIBER_BOT_API_URL, VIBER_BOT_USER_AGENT
from viberbot.api.viber_requests import create_request
from viberbot.api.api_request_sender import ApiRequestSender
from viberbot.api.message_sender import MessageSender

from viberbot import Api


class CustomApiRequestSender(ApiRequestSender):

    def __init__(self, logger, viber_bot_api_url, bot_configuration, viber_bot_user_agent):
        super().__init__(logger, viber_bot_api_url, bot_configuration, viber_bot_user_agent)
        self.session = requests.Session()
        self.session.verify = False

    def post_request(self, endpoint, payload):
        try:
            headers = requests.utils.default_headers()
            headers.update({
                'User-Agent': self._user_agent
            })
            response = self.session.post(self._viber_bot_api_url + '/' + endpoint, data=payload, headers=headers)
            response.raise_for_status()
            return json.loads(response.text)
        except RequestException as e:
            self._logger.error(
                u"failed to post request to endpoint={0}, with payload={1}. error is: {2}"
                .format(endpoint, payload, traceback.format_exc()))
            raise e
        except Exception as ex:
            self._logger.error(
                u"unexpected Exception while trying to post request. error is: {0}"
                .format(traceback.format_exc()))
            raise ex


class CustomApi(Api):
    def __init__(self, bot_configuration):
        self._logger = logging.getLogger('viber.bot.api')
        self._bot_configuration = bot_configuration
        self._request_sender = CustomApiRequestSender(self._logger, VIBER_BOT_API_URL, bot_configuration,
                                                VIBER_BOT_USER_AGENT)
        self._message_sender = MessageSender(self._logger, self._request_sender, bot_configuration)
