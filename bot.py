import os
import time
import random
from datetime import datetime, timezone
import pytz
from colorama import Fore, Style, init
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

os.system('clear' if os.name == 'posix' else 'cls')

import warnings
warnings.filterwarnings('ignore')

import sys
if not sys.warnoptions:
    os.environ["PYTHONWARNINGS"] = "ignore"

init(autoreset=True)

class PsyBot:
    def __init__(self, private_key, proxy=None, captcha_api_key=None):
        self.private_key = private_key
        self.proxy = proxy
        self.captcha_api_key = captcha_api_key
        self.session = requests.Session()
        self.token = None
        
        if self.proxy:
            self.session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        
        self.session.headers.update({
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://psy.xyz',
            'referer': 'https://psy.xyz/',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        })
        
        account = Account.from_key(private_key)
        self.address = account.address
    
    def get_wib_time(self):
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime('%H:%M:%S')
    
    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        
        if level == "INFO":
            color = Fore.CYAN
            symbol = "[INFO]"
        elif level == "SUCCESS":
            color = Fore.GREEN
            symbol = "[SUCCESS]"
        elif level == "ERROR":
            color = Fore.RED
            symbol = "[ERROR]"
        elif level == "WARNING":
            color = Fore.YELLOW
            symbol = "[WARNING]"
        else:
            color = Fore.WHITE
            symbol = "[LOG]"
        
        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")
    
    def get_nonce(self):
        try:
            url = f"https://member-api.psy.xyz/auth/wallet/nonce?address={self.address}&chainType=ethereum"
            response = self.session.get(url)
            data = response.json()
            
            if data['code'] == 0:
                nonce = data['data']['nonce']
                return nonce
            else:
                self.log(f"Failed to get nonce: {data['msg']}", "ERROR")
                return None
        except Exception as e:
            self.log(f"Exception getting nonce: {str(e)}", "ERROR")
            return None
    
    def solve_captcha(self):
        if not self.captcha_api_key:
            self.log("2Captcha API Key not available", "ERROR")
            return None
        
        try:
            site_key = "0x4AAAAAAB4Dnwf7VH4TyqYB"
            website_url = "https://psy.xyz"
            
            self.log("Sending captcha to 2Captcha...", "INFO")
            
            create_task_url = "https://api.2captcha.com/createTask"
            task_data = {
                "clientKey": self.captcha_api_key,
                "task": {
                    "type": "TurnstileTaskProxyless",
                    "websiteURL": website_url,
                    "websiteKey": site_key
                }
            }
            
            response = self.session.post(create_task_url, json=task_data)
            result = response.json()
            
            if result.get('errorId') != 0:
                self.log(f"Error creating task: {result.get('errorDescription')}", "ERROR")
                return None
            
            task_id = result['taskId']
            self.log(f"Task ID: {task_id}", "INFO")
            
            get_result_url = "https://api.2captcha.com/getTaskResult"
            max_attempts = 60
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(3)
                attempt += 1
                
                result_data = {
                    "clientKey": self.captcha_api_key,
                    "taskId": task_id
                }
                
                response = self.session.post(get_result_url, json=result_data)
                result = response.json()
                
                if result.get('status') == 'ready':
                    token = result['solution']['token']
                    self.log(f"Captcha solved successfully!", "SUCCESS")
                    return token
                elif result.get('status') == 'processing':
                    self.log(f"Waiting for captcha solution... ({attempt}/{max_attempts})", "INFO")
                else:
                    self.log(f"Unknown status: {result}", "ERROR")
                    return None
            
            self.log("Timeout waiting for captcha", "ERROR")
            return None
            
        except Exception as e:
            self.log(f"Exception solving captcha: {str(e)}", "ERROR")
            return None
    
    def sign_message(self, nonce):
        try:
            issued_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            
            message = f"""https://psy.xyz wants you to sign in with your Ethereum account:
{self.address}


URI: https://psy.xyz
Version: 1
Chain ID: 1
Nonce: {nonce}
Issued At: {issued_at}"""
            
            w3 = Web3()
            account = Account.from_key(self.private_key)
            message_hash = encode_defunct(text=message)
            signed_message = account.sign_message(message_hash)
            
            signature = signed_message.signature.hex()
            self.log(f"Message signed successfully", "SUCCESS")
            
            return {
                'message': message,
                'signature': signature,
                'issued_at': issued_at
            }
        except Exception as e:
            self.log(f"Exception signing message: {str(e)}", "ERROR")
            return None
    
    def login(self, nonce, signature_data, captcha_token):
        try:
            url = "https://member-api.psy.xyz/auth/wallet/login"
            
            payload = {
                "chainId": 1,
                "chainType": "ethereum",
                "inviteCode": "856EAF8B",
                "message": signature_data['message'],
                "nonce": nonce,
                "signature": signature_data['signature'],
                "token": captcha_token
            }
            
            response = self.session.post(url, json=payload)
            data = response.json()
            
            if data['code'] == 0:
                token = data['data']['token']
                self.token = token
                self.log(f"Login successful!", "SUCCESS")
                return token
            else:
                self.log(f"Login failed: {data['msg']}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Exception during login: {str(e)}", "ERROR")
            return None
    
    def get_user_info(self):
        try:
            url = "https://member-api.psy.xyz/users/me"
            
            headers = {
                'authorization': f'Bearer {self.token}'
            }
            
            response = self.session.get(url, headers=headers)
            data = response.json()
            
            if data['code'] == 0:
                user_data = data['data']
                
                username = user_data.get('username', 'N/A')
                score = user_data.get('score', 0)
                level = user_data.get('level', 'N/A')
                consecutive_days = user_data.get('consecutiveCheckInDays', 0)
                total_referrals = user_data.get('totalReferrals', 0)
                
                self.log(f"Username: {username} | Level: {level}", "INFO")
                self.log(f"Score: {score} | Consecutive Days: {consecutive_days} | Referrals: {total_referrals}", "INFO")
                
                if 'twitterUser' in user_data and user_data['twitterUser']:
                    twitter = user_data['twitterUser']
                    self.log(f"Twitter: @{twitter.get('username', 'N/A')}", "INFO")
                
                if 'discordUser' in user_data and user_data['discordUser']:
                    discord = user_data['discordUser']
                    self.log(f"Discord: {discord.get('username', 'N/A')}", "INFO")
                
                return user_data
            else:
                self.log(f"Failed to get user info: {data['msg']}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Exception getting user info: {str(e)}", "ERROR")
            return None
    
    def check_in(self):
        try:
            url = "https://member-api.psy.xyz/tasks/check-in"
            
            headers = {
                'authorization': f'Bearer {self.token}',
                'content-length': '0'
            }
            
            response = self.session.post(url, headers=headers)
            data = response.json()
            
            if data['code'] == 0:
                check_in_data = data['data']
                
                if check_in_data.get('success'):
                    reward = check_in_data.get('rewardScore', 0)
                    consecutive_days = check_in_data.get('consecutiveDays', 0)
                    
                    self.log(f"Check-in Success! Reward: +{reward} Points | Consecutive Days: {consecutive_days}", "SUCCESS")
                    
                    if check_in_data.get('isSeventhDay'):
                        self.log(f"BONUS! 7th Consecutive Day!", "SUCCESS")
                    
                    return check_in_data
                else:
                    self.log(f"Check-in not successful", "WARNING")
                    return None
            else:
                self.log(f"Check-in failed: {data['msg']}", "WARNING")
                return None
                
        except Exception as e:
            self.log(f"Exception during check-in: {str(e)}", "ERROR")
            return None
    
    def run(self):
        self.log(f"Wallet: {self.address[:6]}...{self.address[-4:]}", "INFO")
        
        proxy_info = self.proxy if self.proxy else "No Proxy"
        self.log(f"Proxy: {proxy_info}", "INFO")
        
        nonce = self.get_nonce()
        if not nonce:
            return False
        
        time.sleep(random.randint(1, 3))
        
        captcha_token = self.solve_captcha()
        if not captcha_token:
            return False
        
        time.sleep(random.randint(1, 3))
        
        signature_data = self.sign_message(nonce)
        if not signature_data:
            return False
        
        time.sleep(random.randint(1, 3))
        
        token = self.login(nonce, signature_data, captcha_token)
        if not token:
            return False
        
        time.sleep(random.randint(1, 3))
        
        user_info = self.get_user_info()
        if not user_info:
            self.log("Failed to get user info, continuing...", "WARNING")
        
        time.sleep(random.randint(1, 3))
        
        check_in_result = self.check_in()
        if not check_in_result:
            self.log("Check-in might already be done today", "WARNING")
        
        return True


def load_file(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def print_banner():
    banner = f"""
{Fore.CYAN}PSY AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
"""
    print(banner)


def show_menu():
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Run with proxy")
    print(f"2. Run without proxy{Style.RESET_ALL}")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    while True:
        try:
            choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
            if choice in ['1', '2']:
                return choice
            else:
                print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")
            exit(0)


def log_message(message, level="INFO"):
    wib = pytz.timezone('Asia/Jakarta')
    time_str = datetime.now(wib).strftime('%H:%M:%S')
    
    if level == "INFO":
        color = Fore.CYAN
        symbol = "[INFO]"
    elif level == "SUCCESS":
        color = Fore.GREEN
        symbol = "[SUCCESS]"
    elif level == "ERROR":
        color = Fore.RED
        symbol = "[ERROR]"
    elif level == "WARNING":
        color = Fore.YELLOW
        symbol = "[WARNING]"
    elif level == "CYCLE":
        color = Fore.MAGENTA
        symbol = "[CYCLE]"
    else:
        color = Fore.WHITE
        symbol = "[LOG]"
    
    print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")


def countdown(seconds):
    for i in range(seconds, 0, -1):
        hours = i // 3600
        minutes = (i % 3600) // 60
        secs = i % 60
        print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 60 + "\r", end="", flush=True)


def main():
    print_banner()
    
    choice = show_menu()
    use_proxy = (choice == '1')
    
    accounts = load_file('accounts.txt')
    if not accounts:
        log_message("No accounts found in accounts.txt", "ERROR")
        log_message("Format: one private key per line", "INFO")
        return
    
    proxies = load_file('proxy.txt') if use_proxy else []
    captcha_keys = load_file('2captcha.txt')
    captcha_api_key = captcha_keys[0] if captcha_keys else None
    
    if not captcha_api_key:
        log_message("2captcha.txt not found or empty", "WARNING")
        log_message("Captcha solving will be skipped", "WARNING")
    
    log_message(f"Loaded {len(accounts)} accounts successfully", "SUCCESS")
    
    if use_proxy and proxies:
        log_message(f"Loaded {len(proxies)} proxies", "SUCCESS")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
    
    cycle = 1
    while True:
        log_message(f"Cycle #{cycle} Started", "CYCLE")
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        success_count = 0
        
        for i, private_key in enumerate(accounts, 1):
            log_message(f"Account #{i}/{len(accounts)}", "INFO")
            
            proxy = None
            if use_proxy and proxies:
                proxy = proxies[(i - 1) % len(proxies)]
            
            bot = PsyBot(private_key, proxy, captcha_api_key)
            
            if bot.run():
                success_count += 1
            
            if i < len(accounts):
                print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                time.sleep(random.randint(2, 5))
        
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        log_message(f"Cycle #{cycle} Complete | Success: {success_count}/{len(accounts)}", "CYCLE")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
        cycle += 1
        
        wait_time = 86400
        countdown(wait_time)


if __name__ == "__main__":
    main()
