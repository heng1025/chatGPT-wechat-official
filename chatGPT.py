import uuid
import configparser

from revChatGPT.V1 import Chatbot, Error

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
            self.chatbot = Chatbot(
                config={
                    "access_token": chatGPT["AccessToken"],
                }
            )

    def sendMessage(self, input):
        try:
            result = "No result!"
            for data in self.chatbot.ask(
                input,
                conversation_id=chatGPT["ConversationId"],
                parent_id=chatGPT["ParentId"],
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
                conversation_id=chatGPT["ConversationId"],
                parent_id=chatGPT["ParentId"],
            ):
                # print log message on terminal screen
                message = data["message"][len(prev_text) :]
                print(message, end="", flush=True)
                prev_text = data["message"]

                # custom  event `chatgpt`
                yield f"id: {uuid.uuid1()}\n".encode("utf-8")
                yield "event: chatgpt\n".encode("utf-8")
                # encode '\n'
                yield f"data: {repr(data['message'])}\n\n".encode("utf-8")
            print()
            yield "event: end\n".encode("utf-8")
        except Error as e:
            logger.error(e.message)
            yield "event: fail\n".encode("utf-8")
            yield f"data: {repr(e)}\n\n".encode("utf-8")
