# syntax=docker/dockerfile:1

# 베이스 이미지
FROM python:3.13-slim

# 파이썬 기본 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리
WORKDIR /app

# 시스템 패키지 최소 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install --no-cache-dir poetry

# 의존성 정의 파일 복사 및 설치
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

# 앱 코드 전체 복사
COPY . .

# 일반 유저로 실행
RUN useradd -m insightbee && chown -R insightbee /app
USER insightbee

# 작업 디렉토리 변경
WORKDIR /app/apps/backend

# Cloud Run 포트
ENV PORT=8080

# FastAPI 실행
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]