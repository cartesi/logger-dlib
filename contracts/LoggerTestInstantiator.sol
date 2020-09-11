// Copyright (C) 2020 Cartesi Pte. Ltd.

// SPDX-License-Identifier: GPL-3.0-only
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


/// @title An instantiator of logger test
pragma solidity ^0.7.0;

import "@cartesi/util/contracts/InstantiatorImpl.sol";
import "@cartesi/util/contracts/Decorated.sol";
import "./LoggerTestInterface.sol";


contract LoggerTestInstantiator is InstantiatorImpl, LoggerTestInterface, Decorated {
    // after construction, the test is in the Idle state and can be changed to Submitting,
    // an hash of the submitted data's root merkle tree will be stored in the contract
    // and then be changed to Downloading state
    // after successful downloading, the state will be changed to Finished

    // IMPLEMENT GARBAGE COLLECTOR AFTER AN INSTACE IS FINISHED!
    struct LoggerTestCtx {
        address user;
        bytes32 submittedHash;
        state currentState;
    }

    mapping(uint256 => LoggerTestCtx) internal instance;

    // These are the possible states and transitions of the contract.

    // +---+
    // |   |
    // +---+
    //   |
    //   | constructor
    //   v
    // +------+
    // | Idle |
    // +------+
    //   |
    //   | claimSubmitting
    //   v
    // +------------+
    // | Submitting |
    // +------------+
    //   |
    //   | claimDownloading
    //   v
    // +-------------+
    // | Downloading |
    // +-------------+
    //   |
    //   | claimFinished
    //   v
    // +----------+
    // | Finished |
    // +----------+

    event LoggerTestCreated(
        uint256 _index,
        address _user
    );
    event LoggerTestFinished(uint256 _index, uint8 _state);

    constructor(
        address _user) {
        currentIndex = 0;
        LoggerTestCtx storage currentInstance = instance[currentIndex];
        currentInstance.user = _user;
        currentInstance.currentState = state.Idle;

        emit LoggerTestCreated(
            currentIndex,
            _user);

        active[currentIndex] = true;
        currentIndex++;
    }

    /// @notice Claim Submitting for the logger test.
    function claimSubmitting(uint256 _index) public
        onlyInstantiated(_index)
        onlyBy(instance[_index].user)
    {
        require(instance[_index].currentState == state.Idle, "The state should be Idle");

        instance[_index].currentState = state.Submitting;
        return;
    }

    /// @notice Claim Downloading for the logger test.
    function claimDownloading(uint256 _index, bytes32 _submittedHash) public
        onlyInstantiated(_index)
        onlyBy(instance[_index].user)
    {
        require(instance[_index].currentState == state.Submitting, "The state should be Submitting");

        instance[_index].currentState = state.Downloading;
        instance[_index].submittedHash = _submittedHash;
        return;
    }

    /// @notice Claim Finished for the logger test.
    function claimFinished(uint256 _index) public override
        onlyInstantiated(_index)
        onlyBy(instance[_index].user)
    {
        require(instance[_index].currentState == state.Downloading, "The state should be Downloading");

        instance[_index].currentState = state.Finished;
        deactivate(_index);
        emit LoggerTestFinished(_index, uint8(instance[_index].currentState));
    }

   function getSubInstances(uint256, address)
        public override pure returns (address[] memory, uint256[] memory)
    {
        address[] memory a = new address[](0);
        uint256[] memory i = new uint256[](0);
        return (a, i);
    }

    function isConcerned(uint256 _index, address _user) public override view returns (bool) {
        return (instance[_index].user == _user);
    }

    function getState(uint256 _index, address) public view returns
        ( address _user,
        bytes32 _hash,
        bytes32 _currentState
        )
    {
        LoggerTestCtx memory i = instance[_index];

        // we have to duplicate the code for getCurrentState because of
        // "stack too deep"
        bytes32 currentState;
        if (instance[_index].currentState == state.Idle) {
            currentState = "Idle";
        }
        if (instance[_index].currentState == state.Submitting) {
            currentState = "Submitting";
        }
        if (instance[_index].currentState == state.Downloading) {
            currentState = "Downloading";
        }
        if (instance[_index].currentState == state.Finished) {
            currentState = "Finished";
        }

        return (
            i.user,
            i.submittedHash,
            currentState
        );
    }

    function getCurrentState(uint256 _index) public override view
        onlyInstantiated(_index)
        returns (bytes32)
    {
        if (instance[_index].currentState == state.Idle) {
            return "Idle";
        }
        if (instance[_index].currentState == state.Submitting) {
            return "Submitting";
        }
        if (instance[_index].currentState == state.Downloading) {
            return "Downloading";
        }
        if (instance[_index].currentState == state.Finished) {
            return "Finished";
        }
        require(false, "Unrecognized state");
    }

    // remove these functions and change tests accordingly
    function stateIsSubmitting(uint256 _index) public view
        onlyInstantiated(_index)
        returns (bool)
    { return instance[_index].currentState == state.Submitting; }

    function stateIsDownloading(uint256 _index) public view
        onlyInstantiated(_index)
        returns (bool)
    { return instance[_index].currentState == state.Downloading; }

    function stateIsFinished(uint256 _index) public view
        onlyInstantiated(_index)
        returns (bool)
    { return instance[_index].currentState == state.Finished; }

    function clearInstance(uint256 _index) internal {
        delete instance[_index].user;
        delete instance[_index].submittedHash;
        deactivate(_index);
    }
}
