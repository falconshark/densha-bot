FROM python:3.12.2
COPY . /app
WORKDIR /app
ENTRYPOINT ["/app/start.sh"]

RUN pip install --upgrade pip\
    && pip install --upgrade setuptools\
    && pip install cryptography \
    && pip install -r requirements.txt
