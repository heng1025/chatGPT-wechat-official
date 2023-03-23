import uuid
from os import getenv

from revChatGPT.typing import Error
from revChatGPT.V1 import Chatbot
from revChatGPT.V3 import Chatbot as ChatbotByApi

from util import getLogger


logger = getLogger("chatGPT")


class ChatGPT:
    _instance = None
    chatbot = None
    api_key = getenv("ApiKey")

    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self) -> None:
        if self.chatbot == None:
            if self.api_key:
                self.chatbot = ChatbotByApi(api_key=self.api_key, proxy=getenv("Proxy"))
            else:
                self.chatbot = Chatbot(
                    config={
                        "proxy": getenv("Proxy"),
                        "access_token": getenv("AccessToken"),
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
                    conversation_id=getenv("ConversationId"),
                    parent_id=getenv("ParentId"),
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
                conversation_id=getenv("ConversationId"),
                parent_id=getenv("ParentId"),
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
