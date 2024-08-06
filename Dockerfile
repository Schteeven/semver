FROM python:3.8-slim

WORKDIR /
RUN python3 -m pip install requests
COPY semantic-version.py .

# CMD ["python", "script.py"]