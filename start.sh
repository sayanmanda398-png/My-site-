#!/bin/bash
echo "Starting PRO Site..."
python app.py &
sleep 2
cloudflared tunnel --protocol http2 --url http://localhost:8080

