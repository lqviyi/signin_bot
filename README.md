需要修改代理地址，可修改配置文件config.json

```
{
  "common":{
    "botToken": "telegram token",
    "botProxy": "http://127.0.0.1:7890",
    "gladosProxyHttp": "socks5://127.0.0.1:7890",
    "gladosProxyHttps": "socks5://127.0.0.1:7890"
  },
  "admin": {
    "chatId": 11111,
    "serverchanId": "",
    "serverchan3Id": ""
  }
}

common 包括telegrambot token以及一些代理ip和端口
admin 可以将服务运行的报错信息同步推送给自己的账号

```

构建镜像

```shell
sudo docker build -t telegram_bot:latest .
```

运行容器

```shell
# 容器运行
sudo docker run -d --name=tgbot -v ./:/app telegram_bot:latest

# 前台运行
sudo docker run -it --name=tgbot -v ./:/app telegram_bot:latest

# 其他根据需要挂载
sudo docker run -d --name=tgbot -v ./user_info.json:/app/user_info.json -v ./logs:/app/logs -v ./config:/app/config telegram_bot:latest

sudo docker run -it --name=tgbot -v ./user_info.json:/app/user_info.json -v ./logs:/app/logs -v ./config:/app/config telegram_bot:latest
```

查看日志

```shell
sudo docker logs tgbot
```

重启

```shell
sudo docker restart tgbot
```

快速删除老的容器/镜像，并构建新的镜像

```shell
sudo docker stop tgbot
sudo docker rm tgbot
sudo docker rmi telegram_bot:latest
sudo docker build -t telegram_bot:latest .
```
