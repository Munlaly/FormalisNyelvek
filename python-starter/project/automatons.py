from typing import override


class Automaton:
    def __init__(
            self,
            states: set[str],
            alphabet: set[str],
            starting_state: str,
            end_states: set[str],
            transitions: dict[str, dict[str, set[str]]]
    ) -> None:
        self.states = states
        self.alphabet = alphabet
        self.starting_state = starting_state
        self.end_states = end_states
        self.transitions = transitions

    @classmethod
    def from_file(cls, input_file: str) -> 'Automaton':
        with open(input_file, 'r') as f:
            lines = f.readlines()

        states = set(lines[0].strip().split())
        alphabet = set(lines[1].strip().split())
        starting_state = lines[2].strip()
        end_states = set(lines[3].strip().split())

        transitions = {}
        for transition in lines[4:]:
            current_state, char, next_state = transition.strip().split()
            if current_state not in transitions:
                transitions[current_state] = {}

            if current_state not in transitions or next_state not in transitions[current_state]:
                raise ValueError(f'Invalid transition: {current_state} --{char}--> {next_state}')
            if char not in alphabet:
                raise ValueError(f'Invalid character in transition: {char} not in alphabet')

            transitions[current_state][char].add(next_state)

        return cls(states, alphabet, starting_state, end_states, transitions)

    def accepts(self, word: str) -> bool:
        current_states = {self.starting_state}
        for char in word:
            next_states = set()
            for state in current_states:
                next_states.update(self.transitions.get(state, {}).get(char, set()))

            if not next_states:
                return False
            current_states = next_states

        return bool(current_states & self.end_states)


class DFA(Automaton):
    def __init__(
            self,
            states: set[str],
            alphabet: set[str],
            starting_state: str,
            end_states: set[str],
            transitions: dict[str, dict[str, set[str]]]
    ) -> None:
        super().__init__(states, alphabet, starting_state, end_states, transitions)

    @classmethod
    @override
    def from_file(cls, input_file: str) -> 'DFA':
        with open(input_file, 'r') as f:
            lines = f.readlines()

        states = set(lines[0].strip().split())
        alphabet = set(lines[1].strip().split())
        starting_state = lines[2].strip()
        end_states = set(lines[3].strip().split())

        transitions = {}
        for transition in lines[4:]:
            current_state, char, next_state = transition.strip().split()
            if current_state not in transitions:
                transitions[current_state] = {}

            if char in transitions[current_state]:
                raise ValueError(f'{current_state} already has a transition for {char}')
            if char not in alphabet:
                raise ValueError(f'Invalid character in transition: {char} not in alphabet')

            transitions[current_state][char] = {next_state}

        return cls(states, alphabet, starting_state, end_states, transitions)

    @override
    def accepts(self, word: str) -> bool:
        current_state = self.starting_state
        for char in word:
            state_transitions = self.transitions.get(current_state, {})
            if char not in state_transitions:
                return False
            current_state = next(iter(state_transitions[char]))

        return current_state in self.end_states
