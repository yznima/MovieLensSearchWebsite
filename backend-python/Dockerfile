FROM python:3

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./boot-dev.sh boot-dev.sh
COPY ./ml-latest-small.zip ml-latest-small.zip
CMD ["./boot-dev.sh"]
