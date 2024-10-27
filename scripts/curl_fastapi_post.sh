#!/bin/bash
curl -X POST "http://localhost:8000/zhopa/" -H "Content-Type: application/json" -d "{\"message\": \"Hello, World\"}"