FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-paho-mqtt ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY monitor.py /app/monitor.py
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python3", "/app/monitor.py"]
