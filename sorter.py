import requests
import json
from datetime import datetime, timezone, timedelta
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_logo():
    logo = """
        ,----,                                                                                                        ,----,                                              
      ,/   .`|     ,----..                                     ,--.                                                 ,/   .`|                                              
    ,`   .'  :    /   /   \     .--.--.         ,---,        ,--.'|     ,---,                      .--.--.        ,`   .'  : ,-.----.       ,---,     ,---,.   .--.--.    
  ;    ;     /   /   .     :   /  /    '.    ,`--.' |    ,--,:  : |   .'  .' `\            ,--,   /  /    '.    ;    ;     / \    /  \   ,`--.' |   ,'  .' |  /  /    '.  
.'___,/    ,'   .   /   ;.  \ |  :  /`. /    |   :  : ,`--.'`|  ' : ,---.'     \         ,'_ /|  |  :  /`. /  .'___,/    ,'  ;   :    \  |   :  : ,---.'   | |  :  /`. /  
|    :     |   .   ;   /  ` ; ;  |  |--`     :   |  ' |   :  :  | | |   |  .`\  |   .--. |  | :  ;  |  |--`   |    :     |   |   | .\ :  :   |  ' |   |   .' ;  |  |--`   
;    |.';  ;   ;   |  ; \ ; | |  :  ;_       |   :  | :   |   \ | : :   : |  '  | ,'_ /| :  . |  |  :  ;_     ;    |.';  ;   .   : |: |  |   :  | :   :  |-, |  :  ;_     
`----'  |  |   |   :  | ; | '  \  \    `.    '   '  ; |   : '  '; | |   ' '  ;  : |  ' | |  . .   \  \    `.  `----'  |  |   |   |  \ :  '   '  ; :   |  ;/|  \  \    `.  
    '   :  ;   .   |  ' ' ' :   `----.   \   |   |  | '   ' ;.    ; '   | ;  .  | |  | ' |  | |    `----.   \     '   :  ;   |   : .  /  |   |  | |   :   .'   `----.   \ 
    |   |  '   '   ;  \; /  |   __ \  \  |   '   :  ; |   | | \   | |   | :  |  ' :  | | :  ' ;    __ \  \  |     |   |  '   ;   | |  \  '   :  ; |   |  |-,   __ \  \  | 
    '   :  |    \   \  ',  /   /  /`--'  /   |   |  ' '   : |  ; .' '   : | /  ;  |  ; ' |  | '   /  /`--'  /     '   :  |   |   | ;\  \ |   |  ' '   :  ;/|  /  /`--'  / 
    ;   |.'      ;   :    /   '--'.     /    '   :  | |   | '`--'   |   | '` ,/   :  | : ;  ; |  '--'.     /      ;   |.'    :   ' | \.' '   :  | |   |    \ '--'.     /  
    '---'         \   \ .'      `--'---'     ;   |.'  '   : |       ;   :  .'     '  :  `--'   \   `--'---'       '---'      :   : :-'   ;   |.'  |   :   .'   `--'---'   
                   `---`                     '---'    ;   |.'       |   ,.'       :  ,      .-./                             |   |.'     '---'    |   | ,'                
                                                      '---'         '---'          `--`----'                                 `---'                `----'                  

                                                                                                                                                                v1
                                                                                                                                                        Account Sorter
    """
    print(logo)

class RobloxScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def make_request(self, url, method="GET", data=None):
        try:
            if method == "GET":
                response = self.session.get(url)
            else:
                response = self.session.post(url, json=data)
            return response if response.status_code == 200 else None
        except:
            return None

    def get_account_details(self, username):
        print(f"Status: Getting user info for {username}...")
        
        user_data = {"usernames": [username], "excludeBannedUsers": True}
        response = self.make_request("https://users.roblox.com/v1/usernames/users", method="POST", data=user_data)
        if not response or not response.json().get('data'):
            return None
        
        user_id = response.json()['data'][0]['id']
        
        print("Status: Checking account details...")
        user_info = self.make_request(f"https://users.roblox.com/v1/users/{user_id}").json()
        verified = user_info.get('hasVerifiedBadge', False)
        
        print("Status: Checking favorites and groups...")
        favorites = self.make_request(f"https://games.roblox.com/v2/users/{user_id}/favorite/games?sortOrder=Asc&limit=100")
        groups = self.make_request(f"https://groups.roblox.com/v1/users/{user_id}/groups/roles")
        
        favorite_count = len(favorites.json().get('data', [])) if favorites else 0
        group_count = len(groups.json().get('data', [])) if groups else 0
        
        print("Status: Checking activity...")
        presence = self.make_request("https://presence.roblox.com/v1/presence/users", method="POST", data={"userIds": [user_id]})
        last_online = presence.json()['userPresences'][0]['lastOnline'] if presence else None
        
        active_recently = False
        if last_online:
            last_online_date = datetime.fromisoformat(last_online.replace('Z', '+00:00'))
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            active_recently = last_online_date > seven_days_ago
        
        return {
            'username': username,
            'user_id': user_id,
            'verified': verified,
            'favorite_count': favorite_count,
            'group_count': group_count,
            'last_online': last_online,
            'active_recently': active_recently
        }

    def check_single_account(self, username):
        print("\n" + "="*50)
        try:
            clean_username = username.split(',')[0].strip()
            details = self.get_account_details(clean_username)
            if not details:
                print(f"Error: Could not find user {clean_username}")
                return
            
            not_verified = not details['verified']
            enough_favorites = details['favorite_count'] >= 5
            is_active = details['active_recently']
            has_groups = details['group_count'] > 0
            
            # Not verified AND (5+ favorites OR recently active) AND has groups
            has_potential = (
                not_verified and
                (enough_favorites or is_active) and
                has_groups
            )
            
            profile_link = f"https://www.roblox.com/users/{details['user_id']}/profile"
            
            if has_potential:
                with open('potential_robux.txt', 'a') as f:
                    f.write(f"{clean_username}, 0, {details['verified']}, {details['favorite_count']}, {details['last_online']}, {details['group_count']}, 0, {profile_link}\n")
            else:
                with open('no_potential.txt', 'a') as f:
                    f.write(f"{clean_username}, 0, {details['verified']}, {profile_link}\n")
            
            print(f"Result: {'✓ Potential' if has_potential else '× No potential'}")
            print("="*50)
            
        except Exception as e:
            print(f"Error checking account: {str(e)}")

    def check_accounts_from_file(self, filename):
        try:
            print("\nPre-scanning accounts from file...")
            unverified_accounts = []
            total_accounts = 0
            
            # First pass: collect unverified accounts by checking the "False" in the file
            with open(filename, 'r') as file:
                for line in file:
                    if line.strip():
                        total_accounts += 1
                        parts = line.strip().split(',')
                        if len(parts) >= 3 and 'false' in parts[2].lower():
                            unverified_accounts.append(line.strip())
            
            total_unverified = len(unverified_accounts)
            print(f"\nFound {total_unverified}/{total_accounts} unverified accounts to process!")
            
            # Second pass: process only unverified accounts
            for index, account in enumerate(unverified_accounts, 1):
                print(f"\nProcessing unverified account {index}/{total_unverified}")
                self.check_single_account(account)
                time.sleep(1)
            
            print(f"\nFinished processing all {total_unverified} unverified accounts!")
                    
        except Exception as e:
            print(f"Error reading file: {str(e)}")

def main():
    scanner = RobloxScanner()
    
    while True:
        clear_screen()
        show_logo()
        print("\n1. Check single account")
        print("2. Check accounts from file")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            username = input("Enter username: ")
            scanner.check_single_account(username)
            input("\nPress Enter to continue...")
        elif choice == "2":
            filename = input("Enter filename: ")
            scanner.check_accounts_from_file(filename)
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            print("Invalid choice")
            time.sleep(1)

if __name__ == "__main__":
    main()