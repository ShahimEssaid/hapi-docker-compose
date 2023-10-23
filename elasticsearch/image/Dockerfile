FROM elasticsearch:7.16.3

# See https://github.com/elastic/dockerfiles/blob/7.16/elasticsearch/Dockerfile

COPY ./root /

ENTRYPOINT ["cw-entrypoint"]

CMD ["eswrapper"]