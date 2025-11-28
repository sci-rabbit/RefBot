FROM python:3.12-slim

WORKDIR /app
COPY . /app/

RUN pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi --directory /app/


ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "alembic upgrade head && python run.py"]