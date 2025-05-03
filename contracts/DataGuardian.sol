// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataGuardian {
    address public owner;
    mapping(string => string) private keys;
    mapping(string => bool) public revoked;
    mapping(string => string) public records; // New: CID to terms mapping

    event KeyStored(string indexed cid, string key);
    event AccessRevoked(string indexed cid);
    event RecordAdded(string indexed cid, string terms);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    function storeKey(string memory cid, string memory key) public onlyOwner {
        require(bytes(cid).length > 0, "CID cannot be empty");
        require(bytes(key).length > 0, "Key cannot be empty");
        keys[cid] = key;
        revoked[cid] = false;
        emit KeyStored(cid, key);
    }

    function getKey(string memory cid) public view returns (string memory) {
        require(!revoked[cid], "Access to this CID has been revoked");
        require(bytes(keys[cid]).length > 0, "No key found for this CID");
        return keys[cid];
    }

    function revokeAccess(string memory cid) public onlyOwner {
        require(bytes(keys[cid]).length > 0, "No key found for this CID");
        revoked[cid] = true;
        delete keys[cid];
        emit AccessRevoked(cid);
    }

    function isRevoked(string memory cid) public view returns (bool) {
        return revoked[cid];
    }

    function addRecord(string memory cid, string memory terms) public onlyOwner {
        require(bytes(cid).length > 0, "CID cannot be empty");
        require(bytes(terms).length > 0, "Terms cannot be empty");
        records[cid] = terms;
        emit RecordAdded(cid, terms);
    }

    function getRecord(string memory cid) public view returns (string memory, address, string memory) {
        require(bytes(records[cid]).length > 0, "No record found for this CID");
        return (cid, owner, records[cid]);
    }
}