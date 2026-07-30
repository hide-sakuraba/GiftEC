FROM python:3.12-slim

# 環境変数の設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /workspace

# pipのアップグレードと依存関係のコピー・インストール
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt
