from project.problem import Problem
import argparse


class CheckProblem(Problem):

    def __init__(self) -> None:
        self.states: list[str] = []
        self.alphabet: list[str] = []
        self.starting_state: str = ''
        self.end_states: list[str] = []
        self.transitions: dict[str, dict[str, str]] = {}

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

    def initialize_automaton(self, input_file: str) -> None:
        with open(input_file, 'r') as f:
            lines = f.readlines()

        self.states = lines[0].strip().split()
        self.alphabet = lines[1].strip().split()
        self.starting_state = lines[2].strip()
        self.end_states = lines[3].strip().split()

        self.transitions = {}
        for transition in lines[4:]:
            current_state, char, next_state = transition.strip().split()
            if current_state not in self.transitions:
                self.transitions[current_state] = {}

            if char in self.transitions[current_state]:
                raise ValueError(f'{current_state} already has a transition for {char}')

            self.transitions[current_state][char] = next_state

    def accepts(self, word: str) -> bool:
        current_state = self.starting_state
        for char in word:
            state_transitions = self.transitions.get(current_state, {})
            if char not in state_transitions:
                return False
            current_state = state_transitions[char]

        return current_state in self.end_states

    def run(self, args) -> None:
        """
        Run the program
        """
        input_file: str = args.input
        output_file: str | None = args.output
        words: list[str] = args.check.split(',')

        self.initialize_automaton(input_file)

        # Checking all words
        with open(output_file, 'w') as f:
            for word in words:
                print('IGEN' if self.accepts(word) else 'NEM', file=f)
