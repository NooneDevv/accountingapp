
FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y git

WORKDIR /src

RUN git clone https://github.com/NooneDevv/accountingapp.git .

# YES?
# RUN GIT_TERMINAL_PROMPT=0 git clone https://github.com/NooneDevv/accountingapp.git .
WORKDIR /src/accounting_project

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=accounting_project.settings

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# This places the contents of 'accountingapp/' into our final '/app' directory
COPY --from=builder /src/accounting_project /app

# Run collectstatic to gather all static files.
# RUN python manage.py collectstatic --noinput

RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# The command to run migrations and start the Gunicorn server.
# This listens on the $PORT from cloud run
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver"]










# ENV DJANGO_APP=accounting_project
# ENV DJANGO_MANAGEMENT_ON_START="migrate --noinput"

# WORKDIR /usr/src/accounting_project
# RUN pip install --upgrade pip 
 
# COPY requirements.txt  /app/
# # RUN pip install -r requirements.txt

# RUN pip install --no-cache-dir -r requirements.txt
# COPY . /app/
 
# # Expose the Django port
# EXPOSE 8000
 
# # Run Django’s development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# # WORKDIR /usr/src/
# # run python manage.py runserver
# # RUN dir
# # EXPOSE 8000
# # CMD ["CD /usr/src/"]
# # ENTRYPOINT [ "python manage.py runserver" ]

# # docker run -d -p 8000:8000 --name accounting-app22 -v C:/Users/tommy/Desktop/final/accountingapp/wow/accountingapp/accounting_project:/src/good -e PIP_INSTALL_ON_START="pip install -r requirements.txt" -e DJANGO_APP=accounting_project.wsgi -e GUNICORN_RELOAD=true -e DJANGO_MANAGEMENT_ON_START="pip3 install -r requirements.txt;migrate --noinput" python