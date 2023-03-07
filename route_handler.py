from chatGPT import ChatGPT
from util import head
from wechat import Bot as WxBot


def wx(method, data, qs):
    if method.lower() == "post" and data:
        # response message
        result = WxBot.receive(data.decode())
        return [result.encode("utf-8")]
    # check token
    bot = WxBot()
    token = bot.check_token(qs)
    return [token.encode("utf-8")]


def chatgpt(method, qs):
    if method.lower() == "get" and qs:
        text = head(qs.get("text"))
        chat_gpt = ChatGPT()
        yield from chat_gpt.sendMessageWithStream(text)
