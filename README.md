# これは何

AWS のcost 通知をするLambda コードの管理場所です。デプロイ方法に関しては変更する予定です。

## Lambda のコードについて
python 3.10

## デプロイ方法について
環境の準備中です.

### Lambda Layer を使用したデプロイ

#### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

#### 2. Lambda Layer の作成
```bash
# Layerディレクトリ構造を作成
mkdir -p layer/python

# 依存関係をLayer用ディレクトリにインストール
pip install -r requirements.txt -t layer/python/

# Layer用のZIPファイルを作成
cd layer
zip -r ../lambda-layer.zip .
cd ..
```

#### 3. AWS CLIでLayerをデプロイ
```bash
# Lambda Layerを作成
aws lambda publish-layer-version \
    --layer-name cost-notify-dependencies \
    --description "Dependencies for cost notification Lambda" \
    --zip-file fileb://lambda-layer.zip \
    --compatible-runtimes python3.10 \
    --region ap-northeast-1
```

#### 4. Lambda関数の作成・更新

### Lambda関数の作成（詳細手順）

#### 1. Lambda関数用のZIPファイル作成
```bash
# 現在のファイルでZIPを作成（依存関係はLayerで管理）
zip lambda-function.zip cost-notfiy.py
```

#### 2. Lambda関数作成のCLIコマンド
```bash
aws lambda create-function \
    --function-name cost-notify-lambda \
    --runtime python3.10 \
    --role arn:aws:iam::YOUR-ACCOUNT-ID:role/lambda-execution-role \
    --handler cost-notfiy.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --description "AWS cost notification Lambda function" \
    --timeout 60 \
    --memory-size 128 \
    --region ap-northeast-1
```

#### 3. 環境変数の設定
```bash
aws lambda update-function-configuration \
    --function-name cost-notify-lambda \
    --environment Variables='{LINEtoken=YOUR_LINE_TOKEN,groupID=YOUR_GROUP_ID}' \
    --region ap-northeast-1
```

#### 4. Lambda Layerを使用する場合
```bash
# 先にLayerを作成（上記のLayer作成手順を参照）
# 関数にLayerを追加
aws lambda update-function-configuration \
    --function-name cost-notify-lambda \
    --layers arn:aws:lambda:ap-northeast-1:YOUR-ACCOUNT-ID:layer:cost-notify-dependencies:1 \
    --region ap-northeast-1
```

**注意点：**
- `YOUR-ACCOUNT-ID`を実際のAWSアカウントIDに置き換えてください
- IAMロールには適切な権限（Lambda実行権限、Cost Explorer API権限など）が必要です
- `YOUR_LINE_TOKEN`と`YOUR_GROUP_ID`を実際の値に置き換えてください


### GitHub Actions を使用したデプロイ


[GitHub Actions lambda deploy](https://github.com/aws-actions/aws-lambda-deploy?tab=readme-ov-file#usage)

## 環境変数
Line Message API を使っているので、以下の環境変数が必要になります。

```bash
LINEtoken
groupID
```

