FROM jwilder/dockerize

ENV BASE /opt/cartesi

RUN apk add --no-cache jq

RUN mkdir -p $BASE/logger/config

WORKDIR $BASE

COPY ./extract-logger-address ./

CMD dockerize \
    -wait file://$BASE/blockchain/contracts/deploy_done \
    -timeout 120s \
    ./extract-logger-address $BASE/blockchain/contracts/Logger.json $BASE/logger/config/address \
    && touch $BASE/logger/config/address_done
