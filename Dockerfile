FROM python:3.7.5-alpine3.9

# install dockerize, as we need to wait on the contract
# address to be extracted
# ----------------------------------------------------
RUN apk add --no-cache openssl musl-dev python3-dev gcc g++ libc-dev
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ENV BASE /opt/cartesi

# Installing python dependencies
# ----------------------------------------------------
COPY ./requirements.txt $BASE/

WORKDIR $BASE

RUN GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS=$(nproc) pip3 install -r requirements.txt

COPY ./manager_server/ $BASE/manager_server
COPY ./logger/ $BASE/logger
COPY ./lib/ $BASE/lib
COPY ./transferred_files $BASE/transferred_files
COPY ./logger-entrypoint.sh $BASE/

EXPOSE 50051

WORKDIR $BASE/lib/grpc-interfaces

RUN ./generate_python_grpc_code.sh

WORKDIR $BASE

CMD dockerize \
    -wait file://$BASE/logger/config/address_done -timeout 120s \
    ./logger-entrypoint.sh
