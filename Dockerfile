FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY main.py .

RUN useradd --no-create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 8080

CMD ["python", "main.py"]
