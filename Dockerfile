FROM postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB postgres
COPY . /repo
COPY populate_db.sql /docker-entrypoint-initdb.d/