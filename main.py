import os
import sys
import requests

from rich import print
from rich.console import Console

import luogu

APP_VERSION = '0.1.0'

def command_help(cmd=None):
    '''获取帮助列表。
    * cmd (可选): 命令名'''
    print(f"Luogu CLI [blue]v{APP_VERSION}[/blue]")
    if cmd is not None:
        if cmd in commands:
            doc = commands[cmd].__doc__ if commands[cmd].__doc__ is not None else '此命令没有帮助。'
            print(f"[bold green]{cmd}[/bold green]: {doc}")
        else:
            print(f"无效的命令 [bold red]{cmd}[/bold red]。")
    else:
        print(f"输入 [green]help <command>[/green] 查看命令帮助。")
        print("可用命令：")
        for cmd in commands:
            doc = commands[cmd].__doc__ if commands[cmd].__doc__ is not None else '\n'
            print(f"  [bold green]{cmd}[/bold green]: {doc.splitlines()[0]}")
        
def check_internet() -> bool:
    '''检查网络连接是否正常。'''
    try:
        requests.get('https://www.luogu.com.cn')
        return True
    except requests.exceptions.ConnectionError:
        return False

commands = {}

online_commands = {
    'help': command_help,
    'csrf': luogu.get_csrf,
    'login': luogu.login,
    'logout': luogu.logout,
    'save': luogu.save,
    'problem': luogu.problem,
}

offline_commands = {
    'help': command_help,
    'problem': luogu.problem_offline,
}

console = Console()

def prompt_header() -> str:
    if luogu.user_log['logged']:
        return f"[bold purple]{luogu.user_log['username']}[/bold purple]:~[green]#[/green] "
    else:
        return "~[green]#[/green] "
    
# Initalization
if len(sys.argv) > 1:
    if check_internet():
        commands = online_commands
        luogu.load_logstate(cmd_only=True)
    else:
        commands = offline_commands
        print("[bold red]无法连接到网络，使用离线模式。[/bold red]")
else:
    print(f"Luogu CLI [blue]v{APP_VERSION}[/blue]")
    print("输入 [bold green]help[/bold green] 查看帮助。")
    if not os.path.exists('saving'):
        os.makedirs('saving')
        os.makedirs('saving/problem')
        os.makedirs('saving/solution')
        os.makedirs('saving/training')
        os.makedirs('saving/discuss')
    if check_internet():
        commands = online_commands
        luogu.pass_js_challenge()
        if not luogu.load_logstate():
            luogu.get_client_id()
            luogu.get_csrf()
            print("您可以使用 [bold green]login[/bold green] 命令登录。")
    else:
        commands = offline_commands
        print("[bold red]无法连接到网络，使用离线模式。[/bold red]")
    print()

if len(sys.argv) > 1:
    cmd = sys.argv[1:]
    # Command Parsing
    if cmd[0] in commands:
        try:
            commands[cmd[0]](*cmd[1:])
        except Exception as e:
            if str(e).find('required positional argument') != -1 and str(repr(e)).find('TypeError') != -1:
                print(f"[bold red]命令 {cmd[0]} 缺少参数。[/bold red]\n输入 [bold green]help {cmd[0]}[/bold green] 查看帮助。")
            else:
                console.print_exception()
                print(f"[bold red]命令 {cmd[0]} 执行时出现错误。[/bold red]")
    else:
        print(f"无效的命令 [bold red]{cmd[0]}[/bold red]。输入 [bold green]help[/bold green] 查看帮助。")
else:
    while True:
        # Prompt Repeats
        print(prompt_header(), end='')
        try:
            prompt = input()
        except KeyboardInterrupt:
            print("输入 [bold red]exit[/bold red] 退出 CLI。")
            continue
        if not prompt:
            continue
        # Command Parsing
        cmd = prompt.split(' ')
        if cmd[0] == 'exit':
            break
        elif cmd[0] in commands:
            try:
                commands[cmd[0]](*cmd[1:])
            except Exception as e:
                if str(e).find('required positional argument') != -1 and str(repr(e)).find('TypeError') != -1:
                    print(f"[bold red]命令 {cmd[0]} 缺少参数。[/bold red]\n输入 [bold green]help {cmd[0]}[/bold green] 查看帮助。")
                else:
                    console.print_exception()
                    print(f"[bold red]命令 {cmd[0]} 执行时出现错误。[/bold red]")
        else:
            print(f"无效的命令 [bold red]{cmd[0]}[/bold red]。输入 [bold green]help[/bold green] 查看帮助。")
        print()
        