FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN pip install peewee
RUN pip install requests
RUN pip install tomlkit

COPY ./app /app

COPY ./traefik.toml /etc/traefik/traefik.toml
COPY ./routes.toml /etc/traefik/routes.toml

RUN python /app/init_db.py 8080 8081
