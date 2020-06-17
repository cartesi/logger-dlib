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


//! A collection of types that represent the manager grpc interface
//! together with the conversion functions from the automatically
//! generated types.

use super::ethereum_types::H256;
use super::logger;
use super::grpc::marshall::Marshaller;

pub const LOGGER_SERVICE_NAME: &'static str = "logger";
pub const LOGGER_METHOD_SUBMIT: &'static str = "/CartesiLogger.Logger/SubmitFile";
pub const LOGGER_METHOD_DOWNLOAD: &'static str = "/CartesiLogger.Logger/DownloadFile";

/// Representation of a request for submitting a log file
#[derive(Debug, Clone)]
pub struct SubmitFileRequest {
    pub path: String,
    pub page_log2_size: u64,
    pub tree_log2_size: u64
}

/// Representation of a request for downloading a log file
#[derive(Debug, Clone)]
pub struct DownloadFileRequest {
    pub path: String,
    pub root: H256,
    pub page_log2_size: u64,
    pub tree_log2_size: u64
}
/// Representation of a response for submitting a log file
#[derive(Debug, Clone)]
pub struct SubmitFileResponse {
    pub root: H256,
    pub status: u32,
    pub progress: u32,
    pub description: String
}

/// Representation of a response for downloading a log file
#[derive(Debug, Clone)]
pub struct DownloadFileResponse {
    pub path: String,
    pub status: u32,
    pub progress: u32,
    pub description: String
}

impl From<logger::SubmitFileResponse>
    for SubmitFileResponse
{
    fn from(
        result: logger::SubmitFileResponse,
    ) -> Self {
        SubmitFileResponse {
            root: H256::from_slice(&result.root
                .into_option()
                .expect("root hash not found")
                .content),
            status: result.status,
            progress: result.progress,
            description: result.description
        }
    }
}

impl From<logger::DownloadFileResponse>
    for DownloadFileResponse
{
    fn from(
        result: logger::DownloadFileResponse,
    ) -> Self {
        DownloadFileResponse {
            path: result.path,
            status: result.status,
            progress: result.progress,
            description: result.description
        }
    }
}

impl From<Vec<u8>>
    for DownloadFileResponse
{
    fn from(
        response: Vec<u8>,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<logger::DownloadFileResponse> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
        marshaller.read(bytes::Bytes::from(response)).unwrap().into()
    }
}

impl From<Vec<u8>>
    for SubmitFileResponse
{
    fn from(
        response: Vec<u8>,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<logger::SubmitFileResponse> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
        marshaller.read(bytes::Bytes::from(response)).unwrap().into()
    }
}

impl From<SubmitFileRequest>
    for Vec<u8>
{
    fn from(
        request: SubmitFileRequest,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<logger::SubmitFileRequest> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
    
        let mut req = logger::SubmitFileRequest::new();
        req.set_path(request.path);
        req.set_page_log2_size(request.page_log2_size);
        req.set_tree_log2_size(request.tree_log2_size);

        marshaller.write(&req).unwrap()
    }
}

impl From<DownloadFileRequest>
    for Vec<u8>
{
    fn from(
        request: DownloadFileRequest,
    ) -> Self {
        let marshaller: Box<dyn Marshaller<logger::DownloadFileRequest> + Sync + Send> = Box::new(grpc::protobuf::MarshallerProtobuf);
    
        let mut req = logger::DownloadFileRequest::new();
        req.set_path(request.path);
        let mut root = logger::Hash::new();
        root.set_content(request.root.to_fixed_bytes().to_vec());
        req.set_root(root);
        req.set_page_log2_size(request.page_log2_size);
        req.set_tree_log2_size(request.tree_log2_size);

        marshaller.write(&req).unwrap()
    }
}
