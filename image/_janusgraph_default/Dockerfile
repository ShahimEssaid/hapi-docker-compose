FROM janusgraph/janusgraph:1.0.0-rc2

ARG USERID=999
ARG GROUPID=999

USER root

COPY ./copy /

RUN usermod -u ${USERID} janusgraph && \
    groupmod -g ${GROUPID} janusgraph && \
    chown -R janusgraph:janusgraph ${JANUS_HOME} ${JANUS_INITDB_DIR} ${JANUS_CONFIG_DIR} ${JANUS_DATA_DIR}

USER janusgraph
