FROM python:3.7.5-alpine3.10 as build-image
ENV BASE /opt/cartesi

RUN apk add --no-cache openssl musl-dev python3-dev gcc g++ libc-dev

WORKDIR $BASE

# Installing python dependencies
# ----------------------------------------------------
COPY ./requirements.txt $BASE/

RUN GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS=$(nproc) pip3 install --user -r requirements.txt

# Generating grpc-interfaces python files
# ----------------------------------------------------
COPY ./grpc-interfaces /root/grpc-interfaces
RUN \
    mkdir -p /root/grpc-interfaces/out \
    && cd /root/grpc-interfaces \
    && python3 -m grpc_tools.protoc -I. \
        --python_out=./out --grpc_python_out=./out \
        core.proto cartesi-base.proto manager-low.proto \
        manager-high.proto logger-high.proto


# Container final image
# ----------------------------------------------------
FROM python:3.7.5-alpine3.10

ENV BASE /opt/cartesi
ENV LOGGER_PATH $BASE/share/logger-server
ENV TIMEOUT 120s

# install dockerize, as we need to wait on the contract
# address to be extracted
# ----------------------------------------------------
RUN apk add --no-cache openssl libstdc++
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR $BASE

# Copy python packages and make sure scripts in .local are usable:
COPY --from=build-image /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p $BASE/bin $BASE/share $BASE/etc/keys $BASE/srv/logger-server/ $LOGGER_PATH/proto

COPY --from=build-image /root/grpc-interfaces/out/*.py $LOGGER_PATH/proto/
COPY ./server/*.py $LOGGER_PATH/
COPY ./logger/ $BASE/share/logger
COPY ./cobra_hdwallet/ $BASE/share/cobra_hdwallet
COPY ./logger-server $BASE/bin/logger-server
COPY ./logger-entrypoint.sh $BASE/bin/logger-entrypoint.sh

EXPOSE 50051

ENTRYPOINT [ "/opt/cartesi/bin/logger-entrypoint.sh", "-a", "0.0.0.0", "-d", "/opt/cartesi/srv/logger-server" ]
