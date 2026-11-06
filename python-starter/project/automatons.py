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

    @override
    def __str__(self) -> str:
        lines = [
            " ".join(sorted(self.states)),
            " ".join(sorted(self.alphabet)),
            self.starting_state,
            " ".join(sorted(self.end_states))
        ]

        transition_list = []
        for state, char_transitions in self.transitions.items():
            for char, next_states in char_transitions.items():
                for next_state in next_states:
                    transition_list.append((state, char, next_state))

        transition_list.sort()

        for state, char, next_state in transition_list:
            lines.append(f"{state} {char} {next_state}")

        return "\n".join(lines)

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
        for char in sorted(automaton.alphabet):
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

def extract_num(state_name: str) -> int:
    digits = ''.join(filter(str.isdigit, state_name))
    return int(digits) if digits else 0

def minimize_hun(dfa:DFA)->DFA:
    pairs: set[frozenset[str]] = {frozenset({p,q}) for p in dfa.states for q in dfa.states if p < q}
    marked_pairs:set[frozenset[str]] = {pair for pair in pairs if len(pair & dfa.end_states) == 1}
    unmarked_pairs: set[frozenset[str]] = pairs - marked_pairs

    changed: bool = True
    while changed:
        changed = False

        for pair in list(unmarked_pairs):
            p, q = tuple(pair)

            for ch in dfa.alphabet:
                p_next = next(iter(dfa.transitions.get(p, {}).get(ch, set())), 'TRAP')
                q_next = next(iter(dfa.transitions.get(q, {}).get(ch, set())), 'TRAP')

                if p_next != q_next and frozenset({p_next, q_next}) in marked_pairs:
                    marked_pairs.add(pair)
                    unmarked_pairs.remove(pair)
                    changed = True
                    break

    equivalent_neighbors: dict[str, set[str]] = {state: set() for state in dfa.states}

    for pair in unmarked_pairs:
        p, q = tuple(pair)
        equivalent_neighbors[p].add(q)
        equivalent_neighbors[q].add(p)

    equivalence_classes: list[frozenset[str]] = []
    unvisited = set(dfa.states)

    while unvisited:
        start_state: str  = unvisited.pop()
        current_class: set[str] = {start_state}
        queue: list[str] = [start_state]

        while queue:
            current: str = queue.pop()
            for neighbor in equivalent_neighbors[current]:
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    current_class.add(neighbor)
                    queue.append(neighbor)

        equivalence_classes.append(frozenset(current_class))

    new_states = set()
    new_end_states = set()
    new_transitions: dict[str, dict[str, set[str]]] = {}

    old_to_new: dict[str, str] = {}

    for eq_class in equivalence_classes:
        smallest_state: str = min(eq_class, key=extract_num)
        new_name:str = f"s{extract_num(smallest_state)}"

        new_states.add(new_name)

        for state in eq_class:
            old_to_new[state] = new_name

    new_starting_state: str = old_to_new[dfa.starting_state]

    for end_state in dfa.end_states:
        if end_state in old_to_new:
            new_end_states.add(old_to_new[end_state])

    for eq_class in equivalence_classes:
        rep:str = next(iter(eq_class))
        new_name:str = old_to_new[rep]

        new_transitions[new_name] = {}
        for char in dfa.alphabet:
            dest_set: set[str] = dfa.transitions.get(rep, {}).get(char, set())

            if dest_set:
                old_dest: str = next(iter(dest_set))
                new_transitions[new_name][char] = {old_to_new[old_dest]}

    return DFA(
        states=new_states,
        alphabet=dfa.alphabet,
        starting_state=new_starting_state,
        end_states=new_end_states,
        transitions=new_transitions
        )
