// Logger DLib is the combination of the on-chain protocol and off-chain
// protocol that work together to store and retreive data from blockchain

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


#![warn(unused_extern_crates)]
pub mod logger_test;
pub mod logger_service;

extern crate error;

#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate log;
extern crate grpc;
extern crate dispatcher;
extern crate ethabi;
extern crate ethereum_types;
extern crate transaction;
extern crate logger_interface;

use grpc::marshall::Marshaller;

pub use logger_test::LoggerTest;
pub use logger_interface::{cartesi_base, logger_high};
pub use logger_service::{
    Hash, FilePath,
    LOGGER_SERVICE_NAME, LOGGER_METHOD_SUBMIT,
    LOGGER_METHOD_DOWNLOAD};

impl From<Vec<u8>>
    for FilePath
{
    fn from(
        response: Vec<u8>,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<logger_high::FilePath> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
        marshaller.read(bytes::Bytes::from(response)).unwrap().into()
    }
}

impl From<Vec<u8>>
    for Hash
{
    fn from(
        response: Vec<u8>,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<cartesi_base::Hash> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
        marshaller.read(bytes::Bytes::from(response)).unwrap().into()
    }
}

impl From<FilePath>
    for Vec<u8>
{
    fn from(
        request: FilePath,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<logger_high::FilePath> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
    
        let mut req = logger_high::FilePath::new();
        req.set_path(request.path);

        marshaller.write(&req).unwrap()
    }
}

impl From<Hash>
    for Vec<u8>
{
    fn from(
        request: Hash,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<cartesi_base::Hash> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
    
        let mut req = cartesi_base::Hash::new();
        req.set_content(request.hash.to_vec());

        marshaller.write(&req).unwrap()
    }
}
