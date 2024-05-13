import sys
import os
import json
import time
import requests
import random
from urllib.parse import unquote
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from colorama import init, Fore, Style

init(autoreset=True)

merah = Fore.LIGHTRED_EX
putih = Fore.LIGHTWHITE_EX
hijau = Fore.LIGHTGREEN_EX
biru = Fore.LIGHTBLUE_EX
reset = Style.RESET_ALL

class OnchainBot:
    def __init__(self):
        self.tg_data = None
        self.bearer = None
        self.peer = "onchaincoin_bot"
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
        )

    def log(self, message):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"{biru}[{current_time}] {message}")

    def login(self, phone):
        session_folder = "session"
        api_id = 2040
        api_hash = "b18441a1ff607e10a989891a5462e627"

        if not os.path.exists(session_folder):
            os.makedirs(session_folder)

        client = TelegramClient(
            f"{session_folder}/{phone}", api_id=api_id, api_hash=api_hash
        )

        try:
            client.connect()
            if not client.is_user_authorized():
                client.send_code_request(phone)
                code = input(f"{putih}input login code : ")
                client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            pw2fa = input(f"{putih}input password 2fa : ")
            client.sign_in(phone=phone, password=pw2fa)

        me = client.get_me()
        first_name = me.first_name
        last_name = me.last_name
        username = me.username
        self.log(f"{putih}Login as {hijau}{first_name} {last_name}")
        res = client(
            RequestWebViewRequest(
                peer=self.peer,
                bot=self.peer,
                platform="Android",
                url="https://db4.onchaincoin.io/",
                from_bot_menu=False,
            )
        )
        self.tg_data = unquote(res.url.split("#tgWebAppData=")[1]).split(
            "&tgWebAppVersion="
        )[0]

    def get_info(self):
        _url = "https://db4.onchaincoin.io/api/info"
        _headers = {
            "user-agent": self.user_agent,
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.5",
            "authorization": f"Bearer {self.bearer}",
            "referer": "https://db4.onchaincoin.io/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers",
            "content-length": "0",
        }
        res = requests.get(_url, headers=_headers, timeout=100)
        if res.status_code != 200:
            self.log(f"{merah}Failed to fetch user info: {res.text}")
            return

        data = res.json().get("user", {})
        name = data.get("fullName", "Unknown")
        energy = data.get("energy", 0)
        clicks = data.get("clicks", 0)
        coins = data.get("coins", 0)

        self.log(f"{hijau}Full name: {putih}{name}")
        self.log(f"{putih}Total coins: {hijau}{coins}")
        self.log(f"{putih}Total clicks: {hijau}{clicks}")
        self.log(f"{putih}Total energy: {hijau}{energy}")
        print("~" * 50)

    def on_login(self):
        _url = "https://db4.onchaincoin.io/api/validate"
        _data = {"hash": self.tg_data}
        _headers = {
            "user-agent": self.user_agent,
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.5",
            "content-type": "application/json",
            "content-length": str(len(json.dumps(_data))),
            "origin": "https://db4.onchaincoin.io",
            "referer": "https://db4.onchaincoin.io/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers",
        }
        res = requests.post(_url, json=_data, headers=_headers, timeout=100)
        if res.status_code != 200:
            self.log(f"{merah}Failed to validate login: {res.text}")
            sys.exit()

        if not res.json().get("success", False):
            self.log(f"{merah}Login validation failed: {res.text}")
            sys.exit()

        self.bearer = res.json().get("token", "")

    def click(self):
        url = "https://db4.onchaincoin.io/api/klick/myself/click"
        _headers = {
            "user-agent": self.user_agent,
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.5",
            "content-type": "application/json",
            "authorization": f"Bearer {self.bearer}",
            "content-length": "12",
            "origin": "https://db4.onchaincoin.io",
            "referer": "https://db4.onchaincoin.io/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "te": "trailers",
        }
        while True:
            try:
                click = random.randint(15, 50)
                _data = {"clicks": click}
                res = requests.post(url, json=_data, headers=_headers, timeout=100)

                if res.status_code != 200:
                    if "Invalid token" in res.text:
                        self.on_login()
                        continue

                if "error" in res.text:
                    self.countdown(self.sleep)
                    continue

                data = res.json()
                clicks = data.get("clicks", 0)
                coins = data.get("coins", 0)
                energy = data.get("energy", 0)

                self.log(f"{hijau}Click: {putih}{click}")
                self.log(f"{hijau}Total clicks: {putih}{clicks}")
                self.log(f"{hijau}Total coins: {putih}{coins}")
                self.log(f"{hijau}Remaining energy: {putih}{energy}")

                if int(energy) < int(self.min_energy):
                    self.countdown(self.sleep)
                    continue

                print("~" * 50)
                self.countdown(self.interval)
                continue

            except requests.RequestException as e:
                self.log(f"{merah}Request error: {e}")
                self.countdown(3)
                continue

    def main(self):
        banner = f"""
    {hijau}Auto tap-tap @onchaincoin_bot
    
    {biru}By t.me/rmndkyl
    github : @rmndkyl{reset}
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print(banner) 

        if not os.path.exists("tg_data"):
            print(f"{putih}Example input: +628169696969")
            phone = input(f"{hijau}Input telegram phone number: {putih}")
            print()
            self.login(phone)

        tg_data = open("tg_data", "r").read()
        self.tg_data = tg_data
        read_config = open("config.json", "r").read()
        load_config = json.loads(read_config)
        self.interval = load_config.get("interval", 60)
        self.sleep = load_config.get("sleep", 60)
        self.min_energy = load_config.get("min_energy", 10)
        self.on_login()
        self.get_info()
        self.click()

if __name__ == "__main__":
    try:
        app = OnchainBot()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
