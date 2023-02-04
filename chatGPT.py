import configparser
from revChatGPT.Official import Chatbot

from util import getLogger


config = configparser.ConfigParser()
config.read("config.ini")
chatGPT = config["chatGPT"]

logger = getLogger("chatGPT")


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

    def sendMessage(self, input):
        try:
            response = self.chatbot.ask(
                input, conversation_id=chatGPT["ConversationId"]
            )
            result = response["choices"][0]["text"]
        except Exception as e:
            result = "Error happend!"
            logger.error(e)

        # log message
        logger.info(f"Q::{input[0:50]}...")
        logger.info(f"A::{result[0:80]}...")

        return result
