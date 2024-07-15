# syntax=docker/dockerfile:1.4
FROM python:3.12

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y gettext snmp nfdump

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

COPY ./init_db.py /usr/src/app/init_db.py
COPY ./wait-for-it.sh /usr/src/app/wait-for-it.sh

RUN chmod +x /usr/src/app/wait-for-it.sh

EXPOSE 8000

CMD ["sh", "-c", "/usr/src/app/wait-for-it.sh db:5432 -- python manage.py migrate && python init_db.py && python manage.py collectstatic --noinput > /dev/null && gunicorn --bind 0.0.0.0:8000 nfstats.wsgi:application"]
