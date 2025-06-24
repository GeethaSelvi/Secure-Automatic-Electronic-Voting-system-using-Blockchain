// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Voting {
    struct Candidate {
        uint id;
        string name;
        string party;
        uint voteCount;
        bool exists;
    }

    mapping(uint => Candidate) public candidates;
    mapping(address => bool) public voters;
    
    address public admin;
    uint public candidateCount;
    uint256 public votingEnd;
    uint256 public votingStart;
    
    event Voted(address indexed voter, uint candidateId);
    event VotingPeriodSet(uint256 start, uint256 end);
    event CandidateRemoved(uint indexed candidateId);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function addCandidate(string memory _name, string memory _party) public onlyAdmin {
        candidateCount++;
        candidates[candidateCount] = Candidate(
            candidateCount,
            _name,
            _party,
            0,
            true
        );
    }

    function removeCandidate(uint _candidateId) public onlyAdmin {
        require(candidates[_candidateId].exists, "Candidate does not exist");
        delete candidates[_candidateId];
        emit CandidateRemoved(_candidateId);
    }

    function vote(uint _candidateId) public {
        require(block.timestamp >= votingStart, "Voting not started");
        require(block.timestamp <= votingEnd, "Voting ended");
        require(_candidateId > 0 && _candidateId <= candidateCount, "Invalid candidate");
        require(!voters[msg.sender], "Already voted");
        
        voters[msg.sender] = true;
        candidates[_candidateId].voteCount++;
        
        emit Voted(msg.sender, _candidateId);
    }

    function setVotingPeriod(uint256 _start, uint256 _end) public onlyAdmin {
        require(_start > block.timestamp, "Start time must be in future");
        require(_end > _start, "End time must be after start");
        require(_end - _start <= 7 days, "Max voting period is 1 week");
        
        votingStart = _start;
        votingEnd = _end;
        emit VotingPeriodSet(_start, _end);
    }

    function getCandidate(uint _id) public view returns (uint, string memory, string memory, uint) {
        Candidate memory c = candidates[_id];
        return (c.id, c.name, c.party, c.voteCount);
    }
}