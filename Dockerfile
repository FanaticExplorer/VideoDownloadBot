FROM python:3.11

WORKDIR /bot/

COPY . /bot/

RUN apt update

RUN apt install ffmpeg -y

RUN pip install -r requirements.txt

RUN pip install -U --pre aiogram

EXPOSE 8443

ENTRYPOINT ["python", "bot.py"]