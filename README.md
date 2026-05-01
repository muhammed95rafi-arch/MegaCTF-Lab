# MegaCTF Lab 🚩

A complete hands-on web security CTF lab with 5 progressive levels. Built with Flask. Runs on Kali Linux, Ubuntu, and Termux.

## Levels

| Level | Topic | Skill |
|-------|-------|-------|
| 1 | File Upload Vulnerability | Upload web shell → RCE |
| 2 | Brute Force Attack | Dictionary attack on login |
| 3 | JWT Token Exploitation | alg:none bypass → privilege escalation |
| 4 | Log Analysis | Read server logs → find attacker + flag |
| 5 | Capture The Flag | Find hidden flag using all skills |

Each level includes Theory, Practical lab, Q&A, and a Flag on completion.

## Setup — Kali Linux / Ubuntu

```bash
git clone https://github.com/muhammed95rafi-arch/mega-ctf-lab
cd mega-ctf-lab
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5000`

## Setup — Termux (Android)

```bash
pkg update && pkg install python
pip install flask werkzeug
python app.py
```

Open: `http://localhost:5000` in browser

## Author

muhammed95rafi-arch | [GitHub](https://github.com/muhammed95rafi-arch) | [TryHackMe](https://tryhackme.com) | [HackerOne](https://hackerone.com)
