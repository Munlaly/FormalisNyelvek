from collections import deque
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

            if char not in alphabet:
                raise ValueError(f'Invalid character in transition: {char} not in alphabet')

            if current_state not in states or next_state not in states:
                raise ValueError(f'Invalid state in transition: {current_state} --{char}--> {next_state}')

            if current_state not in transitions:
                transitions[current_state] = {char:{next_state,}}
            elif char not in transitions[current_state]:
                transitions[current_state][char] = {next_state,}
            else:
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
        base_automaton = super().from_file(input_file)

        for state, transitions in base_automaton.transitions.items():
            for char, next_states in transitions.items():
                if len(next_states) > 1:
                    raise ValueError(
                        f'DFA cannot have multiple transitions for the same character: {state} --{char}--> {next_states}')

        return cls(
            states=base_automaton.states,
            alphabet=base_automaton.alphabet,
            starting_state=base_automaton.starting_state,
            end_states=base_automaton.end_states,
            transitions=base_automaton.transitions
        )

    @override
    def accepts(self, word: str) -> bool:
        current_state = self.starting_state
        for char in word:
            state_transitions = self.transitions.get(current_state, {})
            if char not in state_transitions:
                return False
            current_state = next(iter(state_transitions[char]))

        return current_state in self.end_states


def determinize(automaton:Automaton) ->DFA:
    new_states = {'s0'}
    new_end_states = set()
    new_transitions: dict[str, dict[str, set[str]]] = {}

    initial_state:frozenset[str] = frozenset({automaton.starting_state})
    states_queue:deque[frozenset[str]] = deque([initial_state])
    state_mapping:dict[frozenset[str], str] = {initial_state: 's0'}

    if initial_state.intersection(automaton.end_states):
        new_end_states.add('s0')

    while states_queue:
        current_state = states_queue.popleft()
        current_name = state_mapping[current_state]

        new_transitions[current_name] = {}
        for char in automaton.alphabet:
            next_states:set[str] = set()
            for state in current_state:
                next_states.update(automaton.transitions.get(state,{}).get(char,set()))

            if not next_states:
                continue

            next_states:frozenset[str] = frozenset(next_states)
            if next_states and next_states not in state_mapping:
                state_mapping[next_states] = f's{len(state_mapping)}'
                new_states.add(state_mapping[next_states])
                states_queue.append(next_states)

                if next_states.intersection(automaton.end_states):
                    new_end_states.add(state_mapping[next_states])

            new_transitions[state_mapping[current_state]][char]= {state_mapping[next_states],}

    return DFA(new_states,automaton.alphabet, 's0', new_end_states, new_transitions)

