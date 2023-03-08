import uuid
import configparser

from revChatGPT.V1 import Chatbot, Error
from revChatGPT.V3 import Chatbot as ChatbotByApi

from util import getLogger


config = configparser.ConfigParser()
config.read("config.ini")
chatGPT = config["chatGPT"]
common = config["COMMON"]

logger = getLogger("chatGPT")


class ChatGPT:
    _instance = None
    chatbot = None
    api_key = chatGPT.get("ApiKey")

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        if self.chatbot == None:
            if self.api_key:
                self.chatbot = ChatbotByApi(
                    api_key=self.api_key, proxy=common.get("Proxy")
                )
            else:
                self.chatbot = Chatbot(
                    config={
                        "proxy": common.get("Proxy"),
                        "access_token": chatGPT.get("AccessToken"),
                    }
                )

    def sendMessage(self, input):
        try:
            result = "No result!"
            if self.api_key:
                result = self.chatbot.ask(input)
            else:
                for data in self.chatbot.ask(
                    input,
                    conversation_id=chatGPT.get("ConversationId"),
                    parent_id=chatGPT.get("ParentId"),
                ):
                    result = data["message"]
        except Error as e:
            result = "Error happend!"
            logger.error(e.message)

        # log message
        logger.info(f"Q::{input}")
        logger.info(f"A::{result}")
        print()
        return result

    def sendMessageWithStream(self, input):
        try:
            logger.info(f"Q::{input}")
            prev_text = ""
            for data in self.chatbot.ask(
                input,
                conversation_id=chatGPT.get("ConversationId"),
                parent_id=chatGPT.get("ParentId"),
            ):
                if self.api_key:
                    print(data, end="", flush=True)
                else:
                    # print log message on terminal screen
                    message = data["message"][len(prev_text) :]
                    print(message, end="", flush=True)
                    prev_text = data["message"]

                # custom  event `chatgpt`
                yield f"id: {uuid.uuid1()}\n".encode("utf-8")
                yield "event: chatgpt\n".encode("utf-8")
                # encode '\n'

                yield f"data: {repr(data if self.api_key else data['message'])}\n\n".encode(
                    "utf-8"
                )
            print()
            yield "event: [Done]\n".encode("utf-8")
        except Error as e:
            logger.error(e.message)
            yield "event: fail\n".encode("utf-8")
            yield f"data: {repr(e)}\n\n".encode("utf-8")
