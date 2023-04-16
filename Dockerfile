FROM python:3.11

WORKDIR /bot/

COPY . /bot/

RUN pip install --user -r requirements.txt

EXPOSE 8443

ENTRYPOINT ["python", "bot.py"]