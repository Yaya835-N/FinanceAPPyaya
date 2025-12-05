#!/bin/sh
set -e

CONSUL_HOST=${CONSUL_HOST:-consul}
CONSUL_PORT=${CONSUL_PORT:-8500}
SERVICE_NAME="apotek-price"
SERVICE_ID="${SERVICE_NAME}-$(date +%s)"

cat <<EOF >/tmp/service.json
{
  "Name": "${SERVICE_NAME}",
  "ID": "${SERVICE_ID}",
  "Address": "apotek",
  "Port": 8501,
  "Check": {
    "HTTP": "http://apotek:8501/",
    "Interval": "10s"
  }
}
EOF

curl -X PUT --data @/tmp/service.json http://${CONSUL_HOST}:${CONSUL_PORT}/v1/agent/service/register || true

streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0
