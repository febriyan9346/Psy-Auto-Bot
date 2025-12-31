# PSY Auto Bot

🤖 Automated bot for PSY.xyz daily check-ins and task completion

**Website:** [https://psy.xyz/psychonaut?icode=5969E654](https://psy.xyz/psychonaut?icode=5969E654)

## Features

- ✅ Automatic daily check-in
- 🔐 Wallet-based authentication
- 🛡️ Cloudflare Turnstile captcha solver (2Captcha integration)
- 🔄 Multi-account support
- 🌐 Proxy support
- ⏰ Auto-loop with 24-hour cycle
- 📊 Detailed logging and statistics
- 🎯 Score tracking and level monitoring

## Prerequisites

- Python 3.8 or higher
- 2Captcha API key (for captcha solving)
- Ethereum private keys

## Installation

1. Clone the repository:
```bash
git clone https://github.com/febriyan9346/Psy-Auto-Bot.git
cd Psy-Auto-Bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### 1. Accounts Setup
Create a file named `accounts.txt` in the root directory and add your Ethereum private keys (one per line):
```
0x1234567890abcdef...
0xabcdef1234567890...
```

### 2. 2Captcha API Key
Create a file named `2captcha.txt` and add your 2Captcha API key:
```
your_2captcha_api_key_here
```

Get your API key from: [https://2captcha.com](https://2captcha.com)

### 3. Proxy Setup (Optional)
If you want to use proxies, create a file named `proxy.txt` with your proxy list (one per line):
```
http://username:password@ip:port
socks5://username:password@ip:port
```

## Usage

Run the bot:
```bash
python bot.py
```

You will be prompted to choose:
- **Option 1:** Run with proxy
- **Option 2:** Run without proxy

The bot will:
1. Load all accounts from `accounts.txt`
2. Process each account sequentially
3. Perform daily check-in
4. Display user statistics
5. Wait 24 hours before the next cycle

## File Structure

```
Psy-Auto-Bot/
├── bot.py              # Main bot script
├── accounts.txt        # Private keys (create this)
├── 2captcha.txt        # 2Captcha API key (create this)
├── proxy.txt           # Proxy list (optional)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Requirements.txt

```txt
requests
web3
eth-account
colorama
pytz
```

## Features Breakdown

### Authentication Flow
1. Get nonce from PSY API
2. Sign message with private key
3. Solve Cloudflare Turnstile captcha
4. Login and receive JWT token

### Daily Check-in
- Automatic daily check-in
- Tracks consecutive days
- Displays reward points
- Special bonus for 7-day streak

### User Statistics
- Username and level
- Current score/points
- Consecutive check-in days
- Total referrals
- Connected social accounts (Twitter, Discord)

## Logging

The bot provides colorful, timestamped logs in WIB (Western Indonesian Time):
- 🔵 **INFO**: General information
- 🟢 **SUCCESS**: Successful operations
- 🔴 **ERROR**: Errors and failures
- 🟡 **WARNING**: Warnings
- 🟣 **CYCLE**: Cycle start/completion

## Safety & Best Practices

⚠️ **Important Security Notes:**
- Never share your private keys
- Keep your `accounts.txt` file secure
- Use `.gitignore` to prevent committing sensitive files
- Consider using a dedicated wallet for bot operations
- Use proxies to avoid rate limiting

## Troubleshooting

### Common Issues

**"No accounts found in accounts.txt"**
- Make sure `accounts.txt` exists and contains valid private keys

**"2captcha.txt not found or empty"**
- Create `2captcha.txt` with your API key
- Get an API key from 2captcha.com

**"Captcha solving failed"**
- Check your 2Captcha balance
- Verify your API key is correct
- Check your internet connection

**"Login failed"**
- Verify private key is valid
- Check if captcha was solved successfully
- Ensure proper proxy configuration

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The author is not responsible for any consequences resulting from the use of this software. Always comply with the terms of service of the platforms you interact with.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support Us with Cryptocurrency

You can make a contribution using any of the following blockchain networks:

| Network | Wallet Address |
|---------|---------------|
| **EVM** | `0x216e9b3a5428543c31e659eb8fea3b4bf770bdfd` |
| **TON** | `UQCEzXLDalfKKySAHuCtBZBARCYnMc0QsTYwN4qda3fE6tto` |
| **SOL** | `9XgbPg8fndBquuYXkGpNYKHHhymdmVhmF6nMkPxhXTki` |
| **SUI** | `0x8c3632ddd46c984571bf28f784f7c7aeca3b8371f146c4024f01add025f993bf` |

---

**Made with ❤️ by FEBRIYAN**

**Star ⭐ this repository if you find it helpful!**
