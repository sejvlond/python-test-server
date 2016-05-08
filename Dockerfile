FROM debian:jessie
MAINTAINER Ondřej Šejvl

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y python3 python3-pip python3-jinja2 python3-docopt \
    && pip3 install tornado schema pyyaml pytz

EXPOSE 6789

VOLUME [ \
    "/www/ultimate-server/conf" \
    "/www/ultimate-server/static" \
]

WORKDIR /www/ultimate-server/

COPY conf ./conf/
COPY src ./src/
COPY static ./static/

ENTRYPOINT [ "python3", "/www/ultimate-server/src/server.py" ]
CMD [ "-c", "/www/ultimate-server/conf/server.yaml" ]
