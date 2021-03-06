// Copyright (C) 2020 Cartesi Pte. Ltd.

// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.

// This program is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
// PARTICULAR PURPOSE. See the GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

// Note: This component currently has dependencies that are licensed under the GNU
// GPL, version 3, and so you should treat this component as a whole as being under
// the GPL version 3. But all Cartesi-written code in this component is licensed
// under the Apache License, version 2, or a compatible permissive license, and can
// be used independently under the Apache v2 license. After this component is
// rewritten, the entire component will be released under the Apache v2 license.

use super::dispatcher::{AddressField, Bytes32Field, String32Field};
use super::dispatcher::{Archive, DApp, Reaction};
use super::error::Result;
use super::error::*;
use super::ethabi::Token;
use super::ethereum_types::{Address, H256, U256};
use super::transaction;
use super::transaction::TransactionRequest;
use super::{
    DownloadFileRequest, SubmitFileRequest,
    DownloadFileResponse, SubmitFileResponse,
    LOGGER_METHOD_DOWNLOAD, LOGGER_METHOD_SUBMIT, LOGGER_SERVICE_NAME,
};

pub struct LoggerTest();

// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// these two structs and the From trait below shuld be
// obtained from a simple derive
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#[derive(Serialize, Deserialize)]
struct LoggerTestCtxParsed(
    AddressField,  // user
    Bytes32Field,  // submittedHash
    String32Field, // currentState
);

#[derive(Serialize, Debug)]
struct LoggerTestCtx {
    user: Address,
    submitted_hash: H256,
    current_state: String,
}

impl From<LoggerTestCtxParsed> for LoggerTestCtx {
    fn from(parsed: LoggerTestCtxParsed) -> LoggerTestCtx {
        LoggerTestCtx {
            user: parsed.0.value,
            submitted_hash: parsed.1.value,
            current_state: parsed.2.value,
        }
    }
}

impl DApp<()> for LoggerTest {
    /// React to the logger test contract, Idle/Waiting/Finished
    fn react(
        instance: &state::Instance,
        archive: &Archive,
        _post_payload: &Option<String>,
        _: &(),
    ) -> Result<Reaction> {
        // get context (state) of the logger test instance
        let parsed: LoggerTestCtxParsed =
            serde_json::from_str(&instance.json_data).chain_err(|| {
                format!(
                    "Could not parse logger instance json_data: {}",
                    &instance.json_data
                )
            })?;
        let ctx: LoggerTestCtx = parsed.into();
        trace!("Context for logger (index {}) {:?}", instance.index, ctx);

        match ctx.current_state.as_ref() {
            "Finished" => {
                return Ok(Reaction::Idle);
            }
            _ => {}
        };

        // if we reach this code, the instance is active, check the user
        let user = instance.concern.user_address.clone();
        if user != ctx.user {
            return Err(Error::from(ErrorKind::InvalidContractState(String::from(
                "User is not an user of the test contract",
            ))));
        };
        trace!("User played (index {}) is: {:?}", instance.index, user);

        match ctx.current_state.as_ref() {
            "Idle" => {
                // claim Submitting in logger test contract
                let request = TransactionRequest {
                    concern: instance.concern.clone(),
                    value: U256::from(0),
                    function: "claimSubmitting".into(),
                    data: vec![Token::Uint(instance.index)],
                    strategy: transaction::Strategy::Simplest,
                };
                return Ok(Reaction::Transaction(request));
            }
            "Submitting" => {
                let path = "../test/test_file".to_string();

                trace!("Submitting file: {}...", path);

                let request = SubmitFileRequest {
                    path: path.clone(),
                    page_log2_size: 10,
                    tree_log2_size: 20,
                };

                let processed_response: SubmitFileResponse = archive
                    .get_response(
                        LOGGER_SERVICE_NAME.to_string(),
                        path.clone(),
                        LOGGER_METHOD_SUBMIT.to_string(),
                        request.clone().into(),
                    )?
                    .map_err(|_| {
                        Error::from(ErrorKind::ArchiveInvalidError(
                            LOGGER_SERVICE_NAME.to_string(),
                            path.clone(),
                            LOGGER_METHOD_SUBMIT.to_string(),
                        ))
                    })?
                    .into();

                if processed_response.status != 0 {
                    return Err(Error::from(ErrorKind::ArchiveMissError(
                        LOGGER_SERVICE_NAME.to_string(),
                        path.clone(),
                        LOGGER_METHOD_SUBMIT.to_string(),
                        request.into()
                    )));
                }

                trace!("Submitted! Result: {:?}...", processed_response.root);

                // claim Downloading in logger test contract
                let request = TransactionRequest {
                    concern: instance.concern.clone(),
                    value: U256::from(0),
                    function: "claimDownloading".into(),
                    data: vec![
                        Token::Uint(instance.index),
                        Token::FixedBytes(processed_response.root.to_vec()),
                    ],
                    strategy: transaction::Strategy::Simplest,
                };
                return Ok(Reaction::Transaction(request));
            }
            "Downloading" => {
                let hash = ctx.submitted_hash.clone();
                trace!("Download file for hash: {:?}...", hash);

                let request = DownloadFileRequest {
                    root: hash.clone(),
                    path: "../test/recovered_file".to_string(),
                    page_log2_size: 10,
                    tree_log2_size: 20,
                };

                let processed_response: DownloadFileResponse = archive
                    .get_response(
                        LOGGER_SERVICE_NAME.to_string(),
                        format!("{:x}", hash.clone()),
                        LOGGER_METHOD_DOWNLOAD.to_string(),
                        request.clone().into(),
                    )?
                    .map_err(|_| {
                        Error::from(ErrorKind::ArchiveInvalidError(
                            LOGGER_SERVICE_NAME.to_string(),
                            format!("{:x}", hash.clone()),
                            LOGGER_METHOD_DOWNLOAD.to_string(),
                        ))
                    })?
                    .into();

                    if processed_response.status != 0 {
                        return Err(Error::from(ErrorKind::ArchiveMissError(
                            LOGGER_SERVICE_NAME.to_string(),
                            format!("{:x}", hash.clone()),
                            LOGGER_METHOD_DOWNLOAD.to_string(),
                            request.into()
                        )));
                    }

                trace!("Downloaded! File stored at: {}...", processed_response.path);

                // TODO: compare the original file and downloaded file

                // claim Submitting in logger test contract
                let request = TransactionRequest {
                    concern: instance.concern.clone(),
                    value: U256::from(0),
                    function: "claimFinished".into(),
                    data: vec![Token::Uint(instance.index)],
                    strategy: transaction::Strategy::Simplest,
                };
                return Ok(Reaction::Transaction(request));
            }
            _ => {
                return Ok(Reaction::Idle);
            }
        };
    }

    fn get_pretty_instance(
        instance: &state::Instance,
        _archive: &Archive,
        _: &(),
    ) -> Result<state::Instance> {
        // get context (state) of the logger test instance
        let parsed: LoggerTestCtxParsed =
            serde_json::from_str(&instance.json_data).chain_err(|| {
                format!(
                    "Could not parse logger test instance json_data: {}",
                    &instance.json_data
                )
            })?;
        let ctx: LoggerTestCtx = parsed.into();
        let json_data = serde_json::to_string(&ctx).unwrap();

        let pretty_sub_instances: Vec<Box<state::Instance>> = vec![];

        let pretty_instance = state::Instance {
            name: "LoggerTest".to_string(),
            concern: instance.concern.clone(),
            index: instance.index,
            json_data: json_data,
            sub_instances: pretty_sub_instances,
        };

        return Ok(pretty_instance);
    }
}
