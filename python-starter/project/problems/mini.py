import argparse

from project.automatons import Automaton, minimize_hun, DFA, minimize_hopcroft
from project.problem import Problem


class MinimizeProblem(Problem):
    def __init__(self) -> None:
        pass

    def initialize_parser(self, parser: argparse.ArgumentParser) -> None:
        """
            Initialize the parser with the necessary arguments
        """
        parser.add_argument('--mini', help='determinize an automaton', action='store_true')
        parser.add_argument('--m', help='method for minimizing')
        return

    def is_chosen_problem(self, args) -> bool:
        """
        Check if the problem is chosen
        """
        return bool(args.mini)

    def run(self,args) -> None:
        """
            Runs the code
        """

        input_file:str = args.input
        output_file:str = args.output

        automaton: Automaton = Automaton.from_file(input_file)

        minimized_automaton:DFA = minimize_hopcroft(automaton)

        with open(output_file,'w') as f:
            print(minimized_automaton, file=f)