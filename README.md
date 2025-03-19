# Desha Bot

## 介紹

本プロジェクトは、Desha Bot APIを使用し、電車/私鉄/地下鉄など、様々な路線の遅延情報を監視し、通知するTelegram Botです。

## URL
[https://t.me/desha_unko_bot](https://t.me/desha_unko_bot)

## 設置手順(普通)
1. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```
2. env.example ファイルを編集し、設定を入力する：
```bash
cp .env.example .env
vi .env.example
```
```bash
TELEGRAM_BOT_TOKEN=
API_URL=http://127.0.0.1:8000
MYSQL_HOST=db
MYSQL_DATABASE=densha_bot
MYSQL_USER=densha_bot
MYSQL_PASSWORD=densha_bot
MYSQL_PORT=3306
```

4. データベースを準備する：
```bash
alembic upgrade head
```
4. 起動する：
```bash
python main.py
```

## 設置手順(Docker)
1. env.example ファイルを編集し、設定を入力する：
```bash
cp .env.example .env
vi .env.example
```
```bash
TELEGRAM_BOT_TOKEN=
API_URL=http://127.0.0.1:8000
MYSQL_HOST=db
MYSQL_DATABASE=densha_bot
MYSQL_USER=densha_bot
MYSQL_PASSWORD=densha_bot
MYSQL_PORT=3306
```

2. Docker-Compose を運行する：
docker-compose up --build -d

## 使用方法
以下のコマンドを使用してください。  

/route [route_name] : ルートの遅延情報を表示します。  
/subscribe [route_name] : ルートの遅延情報を監視し、遅延情報を通知します。  
/unsubscribe [route_name] : ルートの遅延情報の監視を解除します。  
/unsubscribe_all : 全てのルートの遅延情報の監視を解除します。  

## Issues
このプロジェクトに問題がある場合や新機能の要望があれば、気軽にIssueまたはPull Requestを作成してください。
