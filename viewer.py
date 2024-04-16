import json

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Label, Markdown, Footer

DIFFICULTIES = ['暂未评定', '入门', '普及-', '普及/提高+', '提高+/省选-', '省选/NOI-', 'NOI/NOI+/CTSC']

with open('lgtags.json', 'r') as f:
    TAGS = json.load(f)

def get_tag_by_id(id):
    for tag in TAGS['tags']:
        if tag['id'] == id:
            return tag
    return None

class ProblemViewer(App):
    BINDINGS = [
        Binding(key="q", action="quit", description="退出查看器"),
    ]

    CSS = """
    .bold {
        text-style: bold;
    }
    .margin {
        margin: 1;
    }
    """

    def __init__(self, problem) -> None:
        self.problem = problem
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            f"[purple bold]提交[/purple bold] {self.problem['totalSubmit']} | \
[purple bold]通过[/purple bold] {self.problem['totalAccepted']} | \
[purple bold]时间限制[/purple bold] {self.problem['limits']['time'][0] if min(self.problem['limits']['time']) == max(self.problem['limits']['time']) else str(min(self.problem['limits']['time']) + ' - ' + max(self.problem['limits']['time']))}ms | \
[purple bold]内存限制[/purple bold] {self.problem['limits']['memory'][0] / 1024 if min(self.problem['limits']['memory']) == max(self.problem['limits']['memory']) else str(min(self.problem['limits']['memory']) / 1024 + ' - ' + max(self.problem['limits']['memory']) / 1024)}MB",
            classes="margin"
        )
        yield Label(f"[purple bold]难度[/purple bold] {DIFFICULTIES[self.problem['difficulty']]}", classes="margin")
        yield Label("", id="history_score", classes="margin")
        yield Label("", id="tags", classes="margin")
        yield Label("[purple bold]题目背景[/purple bold]", classes="bold margin")
        yield Markdown(self.problem['background'], classes="margin")
        yield Label("[purple bold]题目描述[/purple bold]", classes="bold margin")
        yield Markdown(self.problem['description'], classes="margin")
        yield Label("[purple bold]输入格式[/purple bold]", classes="bold margin")
        yield Markdown(self.problem['inputFormat'], classes="margin")
        yield Label("[purple bold]输出格式[/purple bold]", classes="bold margin")
        yield Markdown(self.problem['outputFormat'], classes="margin")
        yield Label("[purple bold]样例[/purple bold]", classes="bold margin")
        yield Markdown("", id="samples", classes="margin")
        yield Label("[purple bold]提示[/purple bold]", classes="bold margin")
        yield Markdown(self.problem['hint'], classes="margin")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "查看题目"
        self.sub_title = f"{self.problem['pid']} {self.problem['title']}"
        # Show score
        if self.problem['showScore']:
            if self.problem['score'] is None:
                self.query_one("#history_score").update(f"[purple bold]历史分数[/purple bold] 暂无分数")
            else:
                self.query_one("#history_score").update(f"[purple bold]历史分数[/purple bold] {self.problem['score']}")
        else:
            if self.problem['accepted']:
                self.query_one("#history_score").update(f"[purple bold]历史分数[/purple bold] AC")
            elif self.problem['submitted']:
                self.query_one("#history_score").update(f"[purple bold]历史分数[/purple bold] WA")
            else:
                self.query_one("#history_score").update(f"[purple bold]历史分数[/purple bold] 暂无分数")
        # Show tags
        tag_text = "[purple bold]题目标签[/purple bold] "
        for tag in self.problem['tags']:
            tag_text += f"[bold]\[{get_tag_by_id(tag)['name']}][/bold] "
        self.query_one("#tags").update(tag_text)
        # Show samples
        samples = self.problem['samples']
        sample_text = ""
        if len(samples) == 0:
            sample_text = "暂无样例。"
        else:
            for i in range(len(samples)):
                sainput = samples[i][0].replace('\\n', '\n')
                saoutput = samples[i][1].replace('\\n', '\n')
                thissample = f"输入 #{i + 1}\n\n```\n{sainput}\n```\n\n输出 #{i + 1}\n\n```\n{saoutput}\n```\n\n"
                sample_text += thissample
        self.query_one("#samples").update(sample_text)

