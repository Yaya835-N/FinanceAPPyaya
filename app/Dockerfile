FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
RUN chmod +x register_service.sh

EXPOSE 8501

ENTRYPOINT ["./register_service.sh"]
