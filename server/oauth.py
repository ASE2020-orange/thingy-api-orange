from github import Github
from dotenv import load_dotenv
import requests
import os

load_dotenv()


def get_github(code):
    # get access token
    url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code,

    }
    headers = {
        "Accept": "application/json"
    }
    r = requests.post(url, data=data, headers=headers)
    answer = r.json()
    access_token = answer["access_token"]
    g = Github(access_token)
    return g


def get_github_auth_url():
    return f"https://github.com/login/oauth/authorize?client_id={os.getenv('GITHUB_CLIENT_ID')}"


if __name__ == '__main__':
    print(get_github_auth_url())
    code = input("code:")
    g = get_github(code)
    u = g.get_user()
    print(u.id, u.name, u.avatar_url)
