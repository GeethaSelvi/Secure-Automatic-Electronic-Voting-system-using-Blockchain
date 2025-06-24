# 🗳️ Secure Automatic Electronic Voting System using Blockchain

A final year engineering project built to improve the **security**, **transparency**, and **trustworthiness** of digital voting using **blockchain technology**.

---

## 📚 Project Overview

Traditional voting systems often face issues like **vote tampering**, **lack of transparency**, and **centralization risks**. This system uses Ethereum **smart contracts** to record each vote immutably, ensuring that every vote counts, and none can be altered.

Voters authenticate using **MetaMask** and cast their vote through a simple web interface. The vote is then **recorded as a blockchain transaction**, verifiable and tamper-proof.

---

## 🧑‍💼 Roles in the System

| Role     | Responsibility                                     |
|----------|-----------------------------------------------------|
| Admin    | Adds voters, candidates, schedules elections        |
| Voter    | Authenticates via MetaMask and casts their vote     |
| Blockchain | Stores the vote permanently using smart contracts |

---

## 🚀 Technologies Used

| Layer         | Technologies |
|---------------|--------------|
| Frontend      | HTML5, CSS3, JavaScript, Bootstrap |
| Backend       | Django (Python), Web3.py |
| Database      | SQLite3 |
| Blockchain    | Solidity, Truffle, Ganache, MetaMask |
| Email OTP     | Brevo (Sendinblue) |

---

## ✨ Key Features

- 🔐 **OTP-based email verification**
- 🦊 **MetaMask authentication for voters**
- 🗳️ **One vote per voter (enforced by smart contract)**
- 📊 **Live result monitoring**
- ⛓️ **Votes stored immutably on Ethereum blockchain**
- ⏱️ **Elections are accessible only during the scheduled time**

---

## 📷 Screenshots

| Feature | Screenshot |
|--------|------------|
| Admin Login | ![](screenshots/admin_login.png) |
| Add Candidates | ![](screenshots/admin_add_candidates.png) |
| Add Voter | ![](screenshots/admin_add_voter.png) |
| Add Schedule | ![](screenshots/admin_add_schedule.png) |
| See Results | ![](screenshots/admin_see_results.png) |
| Voter Signin | ![](screenshots/voter_signin.png) |
| View Candidates | ![](screenshots/voter_view_candidates.png) |
| Connect MetaMask | ![](screenshots/voter_connect_metamask.png) |
| Vote Stored in Blockchain | ![](screenshots/vote_stored_blockchain.png) |

---

## 🧱 Project Structure

project/
├── contracts/ # Solidity Smart Contracts
├── frontend/ # HTML/CSS/JS + Bootstrap templates
├── backend/ # Django backend
│ ├── views/
│ ├── models/
│ └── urls.py
├── screenshots/ # Images for documentation
├── static/
├── manage.py
├── README.md
└── .gitignore

