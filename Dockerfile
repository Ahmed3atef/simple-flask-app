FROM python:3.14-alpine

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apk add --no-cache nano

RUN addgroup -S app && adduser -S app -G app app

USER app

WORKDIR /app

# copy project dependencies files
COPY pyproject.toml uv.lock ./

# copy the app files
COPY . .

RUN mkdir /app/data

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["uv", "run", "flask", "run"]