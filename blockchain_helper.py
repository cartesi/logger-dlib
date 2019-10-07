# Copyright 2019 Cartesi Pte. Ltd.

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import sys
import json
import yaml
import time
import glob
import argparse
import subprocess

# ganache params
GANACHE_OUTPUT_LOG = "./ganache-output.log"
GANACHE_BIN_PATH = "./node_modules/.bin/ganache-cli"
GANACHE_DB_DIR = "ganache_db/"
GANACHE_MNEMONIC = '"mixed bless goat recipe urban pair tuna diet drive capable normal action"'
GANACHE_ACCTKEYS_PATH = "./accts.json"
GANACHE_GAS_LIMIT = "9007199254740991"
GANACHE_DEFAULT_BALANCE = "200000000"
GANACHE_NETWORKS = "7777"
CONTRACT_BUILD_DIR = "build/contracts/"
NUMBER_OF_ACCOUTS = "10"

# truffle params
TRUFFLE_BIN_PATH = "./node_modules/.bin/truffle"

# cartesi files
IS_DEPLOY = False
IS_RUN = False
BLOCKCHAIN_DIR = "blockchain_files/"
DEPLOYED_CONTRACTS_FILE = "deployed_contracts.yaml"
DEPLOYED_CONTRACTS_FILE_PATH = BLOCKCHAIN_DIR + DEPLOYED_CONTRACTS_FILE
CONCERNS_CONTRACTS_FILE = "concerned_contracts.yaml"
CONCERNS_CONTRACTS_FILE_PATH = BLOCKCHAIN_DIR + CONCERNS_CONTRACTS_FILE
WALLETS_FILE = "wallets.yaml"
WALLETS_FILE_PATH = BLOCKCHAIN_DIR + WALLETS_FILE
BASE_CONFIG_FILE = "cartesi_dapp_config.yaml"

def get_args():
    parser = argparse.ArgumentParser(description='Simple helper program to manager the blockchain service, including deploying contracts and starting ganache')
    parser.add_argument('--base_config_file', '-b', dest='base_config_file', help="Specify the name of the cartesi config file to use (Default: cartesi_dapp_config.yaml)")
    parser.add_argument('--deploy', '-d', dest='is_deploy', action='store_true', default=False, help="Deploy contracts to the blockchain (Default: False)")
    parser.add_argument('--run', '-r', dest='is_run', action='store_true', default=False, help="Run ganache (Default: False)")


    args = parser.parse_args()

    global BASE_CONFIG_FILE
    global IS_RUN
    global IS_DEPLOY

    if args.base_config_file:
        BASE_CONFIG_FILE = args.base_config_file

    if (args.is_deploy):
        IS_DEPLOY = True

    if (args.is_run):
        IS_RUN = True

def truffle_migrate(name, path, migrate_from, migrate_to, deployed_cache):
    print("deploying {}...".format(name))
    subprocess.call([TRUFFLE_BIN_PATH, "migrate", "--reset", "-f",
        migrate_from, "--to", migrate_to],
        stdout=subprocess.DEVNULL, cwd=path)
    # export deployed address to DEPLOYED_CONTRACTS_FILE_PATH
    with open(DEPLOYED_CONTRACTS_FILE_PATH, 'w+') as deployed_file:
        deployed = yaml.safe_load(deployed_file) or {}
        for f in glob.glob(CONTRACT_BUILD_DIR + "*.json"):
            contract = os.path.splitext(os.path.basename(f))[0]
            if (deployed is None) or (not contract in deployed.keys()):
                with open(f, 'r') as built_file:
                    built = json.load(built_file)
                    if GANACHE_NETWORKS in built["networks"].keys():
                        deployed[contract] = built["networks"][GANACHE_NETWORKS]["address"]
        yaml.dump(deployed, deployed_file, default_flow_style=False)
    deployed_cache[name] = True

def run():

    global NUMBER_OF_ACCOUTS
    global GANACHE_NETWORKS

    with open(BASE_CONFIG_FILE, 'r') as base_file:
        base = yaml.safe_load(base_file)
        NUMBER_OF_ACCOUTS = str(base["blockchain"]["number_of_accounts"])
        GANACHE_NETWORKS = base["blockchain"]["networks"]

    # start ganache
    print("starting ganache...")
    ganache_proc = subprocess.call([GANACHE_BIN_PATH,
        "--db", GANACHE_DB_DIR, "-l", GANACHE_GAS_LIMIT,
        "-e", GANACHE_DEFAULT_BALANCE, "-i", GANACHE_NETWORKS,
        "-d", "--mnemonic", GANACHE_MNEMONIC,
        "-a", NUMBER_OF_ACCOUTS])

def deploy():
    # clean up ganache db directory
    subprocess.call(["rm", "-rf", GANACHE_DB_DIR])
    subprocess.call(["mkdir", GANACHE_DB_DIR])

    # clean up blockchain directory
    subprocess.call(["rm", "-rf", BLOCKCHAIN_DIR])
    subprocess.call(["mkdir", BLOCKCHAIN_DIR])

    # clean up blockchain build directory
    subprocess.call(["rm", "-rf", CONTRACT_BUILD_DIR])

    # export ENV variables
    os.environ["DEPLOYED_CONTRACTS_FILE_PATH"] = DEPLOYED_CONTRACTS_FILE_PATH
    os.environ["WALLETS_FILE_PATH"] = WALLETS_FILE_PATH

    # creating deployed contracts file
    with open(DEPLOYED_CONTRACTS_FILE_PATH, 'w+') as f:
        yaml.dump({}, f, default_flow_style=False)

    # creating concern contracts file
    with open(CONCERNS_CONTRACTS_FILE_PATH, 'w+') as f:
        yaml.dump([], f, default_flow_style=False)

    with open(BASE_CONFIG_FILE, 'r') as base_file:
        base = yaml.safe_load(base_file)
        NUMBER_OF_ACCOUTS = str(base["blockchain"]["number_of_accounts"])
        GANACHE_NETWORKS = base["blockchain"]["networks"]

    # start ganache
    print("starting ganache...")
    ganache_proc = subprocess.Popen([GANACHE_BIN_PATH,
        "--db", GANACHE_DB_DIR, "-l", GANACHE_GAS_LIMIT,
        "-e", GANACHE_DEFAULT_BALANCE, "-i", GANACHE_NETWORKS,
        "-d", "--mnemonic", GANACHE_MNEMONIC,
        "--acctKeys", GANACHE_ACCTKEYS_PATH,
        "-a", NUMBER_OF_ACCOUTS], stdout=subprocess.DEVNULL)

    # waiting for the output wallets file
    time.sleep(10)

    # export accounts and keys to wallets.yaml
    print("exporting wallets...")
    try:
        with open(GANACHE_ACCTKEYS_PATH) as accts_file:
            accts = json.load(accts_file)
            wallets = []
            with open(WALLETS_FILE_PATH, 'w+') as wallets_file:
                for address, key in accts["private_keys"].items():
                    wallet = {}
                    wallet["address"] = address
                    wallet["key"] = key
                    wallets.append(wallet)
                yaml.dump(wallets, wallets_file, default_flow_style=False)
    except Exception as e:
        print(str(e))
        print("destroying ganache due to unexpected error...")
        ganache_proc.kill()
        exit(1)

    # export wallet ENV variable

    projects = {}
    undeployed_projects = {}
    with open(BASE_CONFIG_FILE, 'r') as base_file:
        projects = yaml.safe_load(base_file)["blockchain"]["projects"]
        undeployed_projects = projects.copy()

    deployed_cache = {}

    # deploy contracts
    print("deploying contracts...")
    try:
        while len(undeployed_projects) > 0:
            number_of_projects = len(undeployed_projects)
            delete_projects_cache = []
            for key, data in undeployed_projects.items():
                if key in deployed_cache:
                    # already deployed_cache, skip
                    continue
                elif len(data["dependencies"]) == 0:
                    # no dependency so migrate immediately
                    truffle_migrate(key, data["path"], data["migrate_from"], data["migrate_to"], deployed_cache)
                    delete_projects_cache.append(key)
                else:
                    ready_to_build = True
                    # check if all dependencies have been deployed
                    for dependency in data["dependencies"]:
                        if not dependency in deployed_cache:
                            # dependency not deployed yet, skip
                            ready_to_build = False
                            break
                    if ready_to_build:
                        # all dependencies deployed
                        truffle_migrate(key, data["path"], data["migrate_from"], data["migrate_to"], deployed_cache)
                        delete_projects_cache.append(key)
            for p in delete_projects_cache:
                undeployed_projects.pop(p, None)
            delete_projects_cache = []
            if number_of_projects == len(undeployed_projects):
                raise Exception("Error! Nothing being deployed, may be missing a dependency?")
    except Exception as e:
        print(str(e))
        print("destroying ganache due to unexpected error...")
        ganache_proc.kill()
        exit(1)

    # write concerns and abis to contract_concerns
    try:
        with open(CONCERNS_CONTRACTS_FILE_PATH, 'w+') as concerns_file:
            with open(DEPLOYED_CONTRACTS_FILE_PATH, 'r') as deployed_file:
                deployed = yaml.safe_load(deployed_file)
                concerns = []
                for key, data in projects.items():
                    for concern in data["concerns"]:
                        # copy abi files
                        abi = data["path"] + CONTRACT_BUILD_DIR + concern + ".json"
                        subprocess.call(["cp", abi, BLOCKCHAIN_DIR])
                        concerns.append({
                            "contract_address": deployed[concern],
                            "abi": abi
                        })
            yaml.dump(concerns, concerns_file, default_flow_style=False)
    except Exception as e:
        print(str(e))
        print("destroying ganache due to unexpected error...")
        ganache_proc.kill()
        exit(1)

    print("destroying ganache...")
    ganache_proc.kill()

    # rm accts.json
    subprocess.call(["rm", GANACHE_ACCTKEYS_PATH])

    print("done!")

get_args()

if IS_DEPLOY:
    deploy()

if IS_RUN:
    run()

if not IS_RUN and not IS_DEPLOY:
    print("please specify at least one mode --run or --deploy")