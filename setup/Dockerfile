FROM cartesi/blockchain-config-generator

# install dockerize, as we need to wait on ganache to be responding
USER root
RUN apk add --no-cache openssl
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

ENV BASE /opt/cartesi
RUN mkdir -p $BASE/logger/config
WORKDIR $BASE
COPY ./address ./

CMD dockerize \
    -wait file://$BASE/blockchain/contracts/deploy_done \
    -timeout 120s \
    blockchain-config-generator -d $BASE/blockchain -i '*' -c Logger -o $BASE/logger/config/address -t ./address -w 120 \
    && touch $BASE/logger/config/address_done
