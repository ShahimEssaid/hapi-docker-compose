FROM postgres:13
# https://github.com/docker-library/postgres/blob/master/13/bookworm/Dockerfile
# https://github.com/docker-library/postgres/blob/master/13/bookworm/docker-entrypoint.sh


RUN apt update; apt install sudo

COPY ./root /

ENTRYPOINT ["cw-entrypoint"]

CMD ["postgres"]
