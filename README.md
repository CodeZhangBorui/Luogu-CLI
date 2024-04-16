# Luogu-CLI

A CLI application for Luogu.

## Examples

Prompt Mode:

```shell
E:\Luogu-CLI ❯ python .\main.py
Luogu CLI v0.1.0
输入 help 查看帮助。
欢迎回来，CodeZhangBorui！
已从 logstate.json 读取用户状态。

CodeZhangBorui:~# help
Luogu CLI v0.1.0
输入 help <command> 查看命令帮助。
可用命令：
  help: 获取帮助列表。
  csrf: 刷新 CSRF Token。
  login: 登录到洛谷。
  logout: 从洛谷退出登录。
  save: 保存洛谷内容（题目、题解、题单、讨论……）以供离线使用。
  problem: 使用可视化查看器查看题目。

CodeZhangBorui:~#
```

Command Mode:

```shell
E:\Luogu-CLI ❯ python .\main.py save problem P1001
已保存 A+B Problem 的内容。
```