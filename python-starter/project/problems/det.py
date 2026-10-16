from project.automatons import Automaton, determinize, DFA
from project.problem import Problem
import argparse

class DeterminizeProblem(Problem):
    def __init__(self) -> None:
        pass

    def initialize_parser(self, parser: argparse.ArgumentParser) -> None:
        """
            Initialize the parser with the necessary arguments
        """
        parser.add_argument('--det', help='determinize an automaton', action='store_true')
        return

    def is_chosen_problem(self, args) -> bool:
        """
        Check if the problem is chosen
        """
        return bool(args.det)

    def run(self, args) -> None:
        """
        Runs the code
        """
        input_file:str = args.input
        output_file:str = args.output

        automaton: Automaton = Automaton.from_file(input_file)

        dfa: DFA = determinize(automaton)

        with open(output_file, 'w') as f:
            print(dfa, file=f)

