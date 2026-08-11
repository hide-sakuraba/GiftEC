FROM python:3.12-slim

# uv バイナリを公式イメージからコピー
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 依存関係のインストール（キャッシュを活用）
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ソースコードのコピー
COPY . .

# 静的ファイルの集約（仮の SECRET_KEY が必要な場合に対応）
RUN SECRET_KEY=dummy python manage.py collectstatic --noinput

# セキュリティ対策: 非 root ユーザーの作成と切り替え
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py createsuperuser --noinput || true && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --access-logfile - --error-logfile -"]