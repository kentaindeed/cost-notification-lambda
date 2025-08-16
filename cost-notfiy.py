#!/usr/bin/env python
# encoding: utf-8

import datetime
import json
import requests
import boto3
import os
import logging
from linebot import LineBotApi
from linebot.models import TextSendMessage

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# LINE の設定
LINETOKEN = os.environ['LINEtoken']
GROUPLINE = os.environ['groupID']

response = boto3.client('cloudwatch', region_name='us-east-1')

get_metric_statistics = response.get_metric_statistics(
    Namespace='AWS/Billing',
    MetricName='EstimatedCharges',
    Dimensions=[
        {
            'Name': 'Currency',
            'Value': 'USD'
        }
    ],
    StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
    EndTime=datetime.datetime.today(),
    Period=86400,
    Statistics=['Maximum'])

cost = get_metric_statistics['Datapoints'][0]['Maximum']
date = get_metric_statistics['Datapoints'][0]['Timestamp'].strftime('%Y年%m月%d日')

def build_message(cost):
    text = "%sまでのAWSの料金は、$%sです。" % (date, cost)
    return text

# line message api で通知
def send_line_message(message):
    """
    LINE Messaging APIを使ってグループにメッセージを送信する関数
    """
    if not LINETOKEN or not GROUPLINE:
        print("LINEのトークンまたはグループIDが設定されていません。")
        return False
        
    line_bot_api = LineBotApi(LINETOKEN)
    
    try:
        line_bot_api.push_message(GROUPLINE, TextSendMessage(text=message))
        print("メッセージを正常に送信しました。")
        return True
    except Exception as e:
        print(f"メッセージの送信に失敗しました: {e}")
        return False

def lambda_handler(event, context):
    message = build_message(cost)
    print(message)
    if send_line_message(message):
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent successfully!')
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to send message.')
        }