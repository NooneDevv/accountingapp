
FROM alang/django:latest

ENV DJANGO_APP=accounting_project
ENV DJANGO_MANAGEMENT_ON_START="migrate --noinput"

WORKDIR /usr/django/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000
