FROM python:3.7.5-alpine3.10 as build-image
ENV BASE /opt/cartesi

RUN apk add --no-cache openssl musl-dev python3-dev gcc g++ libc-dev

WORKDIR $BASE

# Installing python dependencies
# ----------------------------------------------------
COPY ./requirements.txt $BASE/

RUN GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS=$(nproc) pip3 install --user -r requirements.txt

# Generating grpc-interfaces files
# ----------------------------------------------------
RUN mkdir -p ./lib/grpc-interfaces

COPY ./lib/grpc-interfaces $BASE/lib/grpc-interfaces

ENV PATH=/root/.local/bin:$PATH
RUN cd ./lib/grpc-interfaces \
    && ./generate_python_grpc_code.sh


# Container final image
# ----------------------------------------------------
FROM python:3.7.5-alpine3.10
ENV BASE /opt/cartesi

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

RUN mkdir -p ./lib/grpc-interfaces
COPY --from=build-image $BASE/lib/grpc-interfaces/py $BASE/lib/grpc-interfaces/py

COPY ./manager_server/ $BASE/manager_server
COPY ./logger/ $BASE/logger
COPY ./transferred_files $BASE/transferred_files
COPY ./logger-entrypoint.sh $BASE/

EXPOSE 50051

CMD dockerize \
    -wait file://$BASE/logger/config/address_done -timeout 120s \
    -wait file://$BASE/keys/keys_done -timeout 120s \
    ./logger-entrypoint.sh
