FROM python:3.11-alpine3.19
LABEL maintainer="hunsooking"

ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:99

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# pyproject.toml 및 poetry.lock 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치 (가상 환경 생성 및 의존성 설치)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 프로젝트 코드 복사
COPY . .

# /app 디렉토리 및 하위 디렉토리에 django-user 소유권 부여
RUN chown -R django-user:django-user /app

# 필요한 시스템 패키지 설치 
RUN apk add --update --no-cache jpeg-dev 

# 사용자 추가 및 /app 디렉토리 소유권 변경
RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user \
    && chown -R django-user:django-user /app  # /app 디렉토리 소유권 변경

EXPOSE 8000

ARG DEV=false

# Poetry를 통해 실행
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

USER django-user

