FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["hiddify_support_bot"]
