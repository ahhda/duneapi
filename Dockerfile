# Taken from:
# https://dev.to/andre347/how-to-easily-create-a-postgres-database-in-docker-4moj
FROM postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB postgres
COPY . /repo
COPY populate_db.sql /docker-entrypoint-initdb.d/