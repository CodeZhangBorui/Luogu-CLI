from rich import print
from rich.console import Console

import luogu

APP_VERSION = '0.1.0'

def command_help(cmd=None):
    '''获取帮助列表。
    * cmd (可选): 命令名'''
    print(cmd[2])
    print(f"Luogu CLI [blue]v{APP_VERSION}[/blue]")
    if cmd is not None:
        if cmd in commands:
            print(f"[bold green]{cmd}[/bold green]: {commands[cmd].__doc__}")
        else:
            print(f"无效的命令 [bold red]{cmd}[/bold red]。")
    else:
        print(f"输入 [green]help <command>[/green] 查看命令帮助。")
        print("可用命令：")
        for cmd in commands:
            print(f"  [bold green]{cmd}[/bold green]: {commands[cmd].__doc__.splitlines()[0]}")

commands = {
    'help': command_help,
    'csrf': luogu.get_csrf,
    'login': luogu.login,
    'logout': luogu.logout,
}

console = Console()

def prompt_header() -> str:
    if luogu.user_log['logged']:
        return f"[bold purple]{luogu.user_log['username']}[/bold purple]:~[green]#[/green] "
    else:
        return "~[green]#[/green] "
    
# Initalization
print(f"Luogu CLI [blue]v{APP_VERSION}[/blue]")
print("输入 [bold green]help[/bold green] 查看帮助。")
luogu.pass_js_challenge()
if not luogu.load_logstate():
    luogu.get_client_id()
    luogu.get_csrf()
    print("您可以使用 [bold green]login[/bold green] 命令登录。")
print()

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
    