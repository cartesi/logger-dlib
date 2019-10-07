// Dispatcher provides the infrastructure to support the development of DApps,
// mediating the communication between on-chain and off-chain components. 

// Copyright (C) 2019 Cartesi Pte. Ltd.

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



//! A collection of types that represent the manager grpc interface
//! together with the conversion functions from the automatically
//! generated types.

use super::ethereum_types::H256;
use super::cartesi_base;

pub const LOGGER_SERVICE_NAME: &'static str = "logger";
pub const LOGGER_METHOD_SUBMIT: &'static str = "/LoggerManagerHigh.LoggerManagerHigh/SubmitFile";
pub const LOGGER_METHOD_DOWNLOAD: &'static str = "/LoggerManagerHigh.LoggerManagerHigh/DownloadFile";

/// Representation of a request for new session
#[derive(Debug, Clone)]
pub struct FilePath {
    pub path: String
}

impl From<logger_interface::logger_high::FilePath>
    for FilePath
{
    fn from(
        result: logger_interface::logger_high::FilePath,
    ) -> Self {
        FilePath {
            path: result.path,
        }
    }
}

/// Representation of a request for running the machine
#[derive(Debug, Clone)]
pub struct Hash {
    pub hash: H256
}

impl From<cartesi_base::Hash>
    for Hash
{
    fn from(
        result: cartesi_base::Hash,
    ) -> Self {
        Hash {
            hash: H256::from_slice(&result.content)
        }
    }
}
