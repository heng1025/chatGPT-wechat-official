import json
import hashlib
import threading
import configparser
from urllib import parse
import xml.etree.ElementTree as ET

from revChatGPT.Official import Chatbot

from util import getLogger, head, make_request

logger = getLogger("wechat")

config = configparser.ConfigParser()
config.read("config.ini")
wechat = config["wechat"]
chatGPT = config["chatGPT"]


class WXRequest:
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(WXRequest, cls).__new__(cls)
        return cls._instance

    def __init__(self, appid=wechat["Appid"], secret=wechat["Secret"]) -> None:
        try:
            self.__checkKey(appid, secret)
            self.appid = appid
            self.secret = secret
        except ValueError as e:
            logger.error(e)

    def sendCustomMessage(self, user, content):
        url = f"{self.BASE_URL}/message/custom/send?access_token={self.__token}"
        data = {
            "touser": user,
            "msgtype": "text",
            "text": {"content": content},
        }
        data = json.dumps(data, ensure_ascii=False).encode()
        make_request(url, method="POST", data=data)

    @property
    def __token(self):
        query = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret,
        }
        url = f"{self.BASE_URL}/token?{parse.urlencode(query)}"
        data = make_request(url, method="GET")
        return data.get("access_token")

    @staticmethod
    def __checkKey(appid, secret):
        if not (appid and secret):
            raise ValueError("WeixinAuthSign: Invalid key")


class ChatGPT:
    _instance = None
    chatbot = None

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        if self.chatbot == None:
            try:
                self.chatbot = Chatbot(api_key=chatGPT["ApiKey"])
            except Exception as e:
                logger.error(f"chatGPT err: {e}")
                raise ValueError(e)


class Bot:
    def __init__(self, salt=wechat["Salt"]) -> None:
        self.salt = salt

    @staticmethod
    def sendChatGPTMessageByApi(input, user):
        try:
            chat_gpt = ChatGPT()
            response = chat_gpt.chatbot.ask(
                input, conversation_id=chatGPT["ConversationId"]
            )
            result = response["choices"][0]["text"]
        except Exception as e:
            result = "Error happend!"
            logger.error(e)
        wxReq = WXRequest()
        logger.info(f"{user.center(80,'-')}")
        logger.info(f"Q::{input[0:50]}...")
        logger.info(f"A::{result[0:80]}...")
        logger.info(f"{'-'.center(80,'-')}")
        wxReq.sendCustomMessage(user, result)

    @staticmethod
    def receive(data):
        root = ET.fromstring(data)
        info_from_user = {}
        for child in root:
            info_from_user[child.tag] = child.text

        MsgType = info_from_user.get("MsgType")
        FromUserName = info_from_user.get("FromUserName")
        ToUserName = info_from_user.get("ToUserName")
        Content = info_from_user.get("Content")
        if MsgType == "text" and Content:
            # must respone to wechat server in 5 seconds
            # https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
            task = lambda: Bot.sendChatGPTMessageByApi(Content, FromUserName)
            chatThread = threading.Thread(target=task, name="chatThread")
            chatThread.start()
            # either return "sucess" or return "" 
            return Bot.gen_response(FromUserName, ToUserName, "正在组织语言(10s+)...")
        return "success"

    @staticmethod
    def gen_response(from_user, to_user, content):
        return (
            "<xml>"
            f"<ToUserName><![CDATA[{from_user}]]>"
            f"</ToUserName><FromUserName><![CDATA[{to_user}]]>"
            "</FromUserName><CreateTime>{int(time.time())}</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            f"<Content><![CDATA[{content}]]></Content>"
            "</xml>"
        )

    def check_token(self, data):
        signature = head(data.get("signature"))
        timestamp = head(data.get("timestamp"))
        nonce = head(data.get("nonce"))
        echostr = head(data.get("echostr"))

        sha1 = hashlib.sha1()
        for param in [nonce, timestamp, self.salt]:
            sha1.update(param.encode("utf-8"))
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr
        raise "Auth Fail"
