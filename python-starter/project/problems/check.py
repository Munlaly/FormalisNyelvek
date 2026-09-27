from wsgiref.types import InputStream

from project.problem import Problem
import argparse


class CheckProblem(Problem):

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
        input_file: InputStream = args.input
        output_file: str | None = args.output
        words:list[str] = args.check.split(',')

        # Initializing the automaton
        with open(input_file, 'r') as f:
            lines = f.readlines()

        states: list[str] = lines[0].strip().split()
        abc: list[str] = lines[1].strip().split()
        starting_state: str = lines[2].strip()
        end_states: list[str] = lines[3].strip().split()

        transitions: dict[str, dict[str, str]] = {}
        for transition in lines[4:]:
            current_state, char, next_state = transition.strip().split()
            transitions[current_state] = {}

            if char in transitions[current_state]:
                raise ValueError(f'{current_state} already has a transition for {char}')

            transitions[current_state][char] = next_state

        # Checking all words
        with open(output_file, 'w') as f:
            for word in words:
                current_state:str = starting_state
                invalid_transition: bool = False
                for char in word:
                    if char not in transitions[current_state].keys():
                        invalid_transition = True
                        break

                    current_state = transitions[current_state][char]

                if invalid_transition:
                    print('NEM', file=f)
                    continue
                if current_state in end_states:
                    print('IGEN', file=f)
                else:
                    print('NEM', file=f)




