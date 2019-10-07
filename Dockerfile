FROM ubuntu:18.04

MAINTAINER Stephen Chen<stephen@cartesi.io>

ENV BASE /opt/cartesi
ENV GANACHE_DB_DIR /opt/cartesi/ganache_db

# Install basic development tools
# ----------------------------------------------------
RUN \
    apt-get update && \
    apt-get install --no-install-recommends -y \
        ca-certificates git build-essential make curl \
        software-properties-common python3 python3-pip \
        python3-setuptools python3-wheel python3-dev

#Install node
SHELL ["/bin/bash", "-c"]
RUN \
    apt-get install -y gnupg-agent && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y nodejs

# Installing contracts dependencies
# ----------------------------------------------------
WORKDIR $BASE/

COPY ./truffle.js $BASE/
COPY ./package.json $BASE/

RUN \
    npm install

# Installing python dependencies
# ----------------------------------------------------
COPY ./requirements.txt $BASE/

RUN \
    pip3 install -r requirements.txt

# Deploying the contracts in ganache and saving it's state
# ----------------------------------------------------
COPY ./dispatcher_config_generator.py $BASE/
COPY ./blockchain_helper.py $BASE/
COPY ./contracts/ $BASE/contracts
COPY ./migrations/ $BASE/migrations
COPY ./make_dispatcher_configs.sh $BASE/
COPY ./cartesi_dapp_config.yaml $BASE/

RUN \
    python3 blockchain_helper.py --deploy

# Generating the config files for dispatcher
# ----------------------------------------------------
RUN \
    ./make_dispatcher_configs.sh

CMD \
    ./node_modules/.bin/ganache-cli --db=$GANACHE_DB_DIR -l 9007199254740991 -e 200000000 -i=7777 -d -h 0.0.0.0 --mnemonic="mixed bless goat recipe urban pair tuna diet drive capable normal action