import requests
import json
import datetime
import base64
import os
from time import sleep
from rich import print
from PIL import Image # pip install pillow

import viewer

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
    'referer': 'https://www.luogu.com.cn/',
    'x-luogu-type': 'content-only',
    'x-csrf-token': '',
    'x-csrf-expires': '',
}

cookies = {}

user_log = {
    'logged': False,
    'username': '',
}

base_url = 'https://www.luogu.com.cn'

def pass_js_challenge() -> bool:
    '''使用字符串操作通过 JavaScript 验证。'''
    res = request('/')
    while res.text.find('C3VK') != -1:
        html = res.text
        c3vk = html.split('.cookie="C3VK=')[1].split(';')[0]
        cookies['C3VK'] = c3vk
        res = requests.get(base_url, headers=headers, cookies=cookies)
    return True

def request(url: str, method: str = 'GET', data: dict = None) -> requests.Response:
    if method == 'GET':
        res = requests.get(base_url + url, headers=headers, cookies=cookies)
    elif method == 'POST':
        res = requests.post(base_url + url, headers=headers, cookies=cookies, data=data)
    else:
        raise NotImplementedError
    return res

def current_user() -> dict:
    '''获取当前登录用户的信息。'''
    res = request('/problem/list')
    data = res.json()
    try:
        return {
            'logged': True,
            'userdata': data['currentUser'],
        }
    except KeyError:
        return {
            'logged': False,
        }

def load_logstate(cmd_only=False) -> bool:
    '''从 logstate.json 中获取上次登录信息。'''
    global cookies
    try:
        with open('logstate.json', 'r') as file:
            logstate = json.loads(file.read())
            cookies = logstate['cookies']
            headers = logstate['headers']
            if not cmd_only:
                data = current_user()
                user_log['logged'] = True
                user_log['username'] = data['userdata']['name']
                print(f"[bold yellow]欢迎回来，{user_log['username']}！[/bold yellow]")
                print(f"已从 [bold blue]logstate.json[/bold blue] 读取用户状态。")
            return True
    except:
        return False

def get_client_id() -> str:
    '''获取一个新的 Client ID。'''
    global cookies
    res = request('/')
    try:
        del cookies['__client_id']
        del cookies['_uid']
    except KeyError:
        pass
    set_cookie = res.headers['Set-Cookie']
    client_id = set_cookie.split('__client_id=')[1].split(';')[0]
    print(f"获得客户端 ID: [bold blue]{client_id}[/bold blue].")
    cookies['__client_id'] = client_id
    cookies['_uid'] = '0'
    return client_id

def get_csrf() -> str:
    '''刷新 CSRF Token。'''
    global headers
    if user_log['logged']:
        print("您已经登录，无需获取 CSRF Token。")
        return headers['x-csrf-token']
    headers['x-csrf-token'] = ''
    res = request('/')
    html = res.text
    csrf_obj = html.split('<meta name="csrf-token" content="')[1].split('"')[0]
    headers['x-csrf-token'] = csrf_obj
    csrf_expires_formatted = datetime.datetime.fromtimestamp(int(csrf_obj.split(':')[0])).strftime('%m-%d %H:%M:%S')
    print(f"刷新 CSRF Token: [bold blue]{csrf_obj}[/bold blue]，过期时间 [bold blue]{csrf_expires_formatted}[/bold blue].")
    return csrf_obj[1]

def lg_captcha() -> str:
    '''获取验证码图片并要求用户输入。'''
    res = request('/lg4/captcha')
    with open('captcha.jpg', 'wb') as file:
        file.write(res.content)
    image = Image.open('captcha.jpg')
    image.show()
    print("验证码图片已保存至 [bold blue]captcha.jpg[/bold blue].")
    captcha = input("请输入验证码: ")
    os.remove('captcha.jpg')
    return captcha

def login(username, password) -> bool:
    '''登录到洛谷。
    * username: 用户名
    * password: 密码'''
    global user_log
    if user_log['logged']:
        print(f"你已经已 [bold blue]{user_log['username']}[/bold blue] 登陆了。输入 [bold green]logout[/bold green] 退出。")
        return True
    global cookies
    captcha = lg_captcha()
    res = request('/do-auth/password', 'POST', {
        'username': username,
        'password': password,
        'captcha': captcha
    })
    data = res.json()
    try:
        uid = res.cookies['_uid']
        username = data['username']
    except KeyError:
        print(f"[bold red]登录失败[/bold red]：{data['currentData']['errorMessage']}")
        return False
    cookies['_uid'] = uid
    user_log['logged'] = True
    user_log['username'] = username
    print(f"[bold yellow]欢迎回来，{username}！[/bold yellow]")
    # Save cookies
    with open('logstate.json', 'w') as file:
        file.write(json.dumps({
            'headers': headers,
            'cookies': cookies,
        }))
    return True

def logout() -> bool:
    '''从洛谷退出登录。'''
    global user_log
    global cookies
    if user_log['logged'] == False:
        print("你还没有登录。")
        return False
    res = request('/auth/logout')
    user_log['logged'] = False
    user_log['username'] = ''
    cookies['_uid'] = '0'
    os.remove('logstate.json')
    print("成功退出登录。")
    get_client_id()
    get_csrf()
    return True

def save(stype, id) -> None:
    '''保存洛谷内容（题目、题解、题单、讨论……）以供离线使用。
    * stype: 类型（problem, solution, training, discuss
    * id: ID'''
    urlmap = {
        'problem': '/problem/{id}',
        'solution': '/problem/{id}/solution',
        'training': '/training/{id}',
        'discuss': '/discuss/{id}',
    }
    res = request(urlmap[stype].format(id=id))
    try:
        data = res.json()
    except json.JSONDecodeError:
        if res.text.find("Your current behavior is detected as abnormal, Please try again later...") != -1:
            print(f"[bold red]错误[/bold red]：触发洛谷限制：Your current behavior is detected as abnormal, Please try again later...")
            print("等待 10 秒后重试。")
            sleep(10)
            save(stype, id)
        else:
            print(f"[bold red]错误[/bold red]：无法解析 JSON 数据。")
            print(res.text)
        return
    if data['code'] != 200:
        print(f"[bold red]错误[/bold red]：{data['currentData']['errorMessage']}")
        return
    with open(f'saving/{stype}/{id}.json', 'w') as f:
        f.write(json.dumps(data['currentData']))
    print(f"已保存 [bold blue]{data['currentTitle']}[/bold blue] 的内容。")
        
def problem(pid) -> None:
    '''使用可视化查看器查看题目。
    * pid: 题目 ID'''
    res = request('/problem/' + pid)
    data = res.json()
    if data['code'] != 200:
        print(f"[bold red]错误[/bold red]：{data['currentData']['errorMessage']}")
        return
    view = viewer.ProblemViewer(problem=data['currentData']['problem'])
    view.run()
    
def problem_offline(pid) -> None:
    '''使用可视化查看器查看题目。
    * pid: 题目 ID'''
    try:
        with open(f'saving/problem/{pid}.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"找不到题目 [bold red]{pid}[/bold red] 的缓存文件。")
        return
    view = viewer.ProblemViewer(problem=data['problem'])
    view.run()