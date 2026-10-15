from project.problem import Problem
from project.automatons import DFA
import argparse


class CheckProblem(Problem):

    def __init__(self) -> None:
        super().__init__()


    def initialize_parser(self, parser: argparse.ArgumentParser) -> None:
        """
            Initialize the parser with the necessary arguments
        """
        parser.add_argument('--check', help='recognize a word')
        return

    def is_chosen_problem(self, args) -> bool:
        """
        Check if the problem is chosen
        """
        return bool(args.check)


    def run(self, args) -> None:
        """
        Run the program
        """
        input_file: str = args.input
        output_file: str | None = args.output
        words: list[str] = args.check.split(',')

        self.automaton = DFA.from_file(input_file)

        # Checking all words
        with open(output_file, 'w') as f:
            for word in words:
                print('IGEN' if self.automaton.accepts(word) else 'NEM', file=f)
