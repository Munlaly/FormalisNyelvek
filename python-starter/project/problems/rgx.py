import argparse
import re
from typing import Callable


from project.problem import Problem

HEAD = r'^\S+ \S+ +\d+ +\d+ '

TASK1_PATTERNS = [
    r'^10-15 ',
    r'^10-15 10:18:51\.',
    r'^\S+ \d\d:\d\d:51\.',
    HEAD + r'[IDVEFAW] lowmemorykiller *:',
    r'^\S+ 10:18:51\.\d+ +221 +\d+ ',
    HEAD + r'E ',
    HEAD + r'W PackageManager:',
    HEAD + r'D [^:]*ExoPlayer[^:]*:',
    HEAD + r'[EW] .*\.java:',
    HEAD + r'[IDVEFAW] (.+?):.*Thread.*',
]

TASK2_PATTERN = re.compile(HEAD + r'E .*\((\w+\.java):\d+\)')

TASK3_PATTERN = re.compile(r'^\S+ \S+ +(\d+) ')

TASK4_PATTERN = re.compile(r'^\S+ \S+ +(\d+) +\d+ E ')
def task1(lines: list[str]) -> list[str]:
    return [str(sum(1 for line in lines if re.search(p, line)))
            for p in TASK1_PATTERNS]

def task2(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        m = TASK2_PATTERN.search(line)
        if m is not None:
            result.append(m.group(1))
    return result

def task3(lines: list[str]) -> list[str]:
    seen = set()
    result = []
    for line in lines:
        m = TASK3_PATTERN.search(line)

        if m is not None:
            pid = m.group(1)
            if pid not in seen:
                seen.add(pid)
                result.append(pid)

    return result

def task4(lines: list[str]) -> list[str]:
    pids = {}
    for line in lines:
        m = TASK4_PATTERN.search(line)
        if m is not None:
            pid = m.group(1)
            pids[pid] = pids.get(pid, 0) + 1

    selected_pid = max(pids, key=pids.get)

    return [f'{selected_pid}={pids[selected_pid]} ({pids[selected_pid]} errors)']

class RegexProblem(Problem):
    def initialize_parser(self, parser: argparse.ArgumentParser) -> None:
        """
            Initialize the parser with the necessary arguments
        """
        parser.add_argument('--rgx', help='solve regex problems', action='store')
        return

    def is_chosen_problem(self, args) -> bool:
        """
        Check if the problem is chosen
        """
        return args.rgx is not None



    def run(self,args) -> None:
        input_file:str = args.input
        output_file:str = args.output
        task_num:int = int(args.rgx) - 1
        tasks:list[Callable] = [task1, task2, task3, task4]

        with open(input_file, 'r', encoding='utf-8') as f_in:
            lines = f_in.read().splitlines()

        result = tasks[task_num](lines)

        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write('\n'.join(result) + '\n')

