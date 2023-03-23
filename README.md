## WeChat official access chatGPT

### dev

1.  create venv `python -m venv .venv`
2.  rename `.env.example` to `.env`
3.  run `pip install -U -r requirements.txt`
4.  run `python main.py`

### deploy

1.  run `docker compose build`
2.  run `docker compose up -d`

### note

-   [Customer Service API - Send Message](https://developers.weixin.qq.com/doc/offiaccount/en/Message_Management/Service_Center_messages.html) permission is required
-   The URL that responds to the wechat server is `http[s]://{YOUR DOMAIN}/wx`
-   We can request an API [Test Account](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
-   For wechat offical configuration please refer to [here](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Access_Overview.html)
-   For chatGPT configuration please refer to [here](https://github.com/acheong08/ChatGPT/blob/main/README.md)

### credit

-   [ChatGPT for python](https://github.com/acheong08/ChatGPT)

### demo

<img src="http://oss.1r21.cn/wx-test.jpg" alt="wechat test account" style="width:200px;"/>
