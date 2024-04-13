FROM python:3.10

ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt

ADD engine /app/engine
ADD workflows /app/workflows
ADD cacert.pem /etc/cacert.pem

RUN useradd ilvk && chown -R ilvk:ilvk /app/workflows

WORKDIR /app
ADD entrypoint.sh /entrypoint.sh

ENTRYPOINT ["bash", "/entrypoint.sh"]
