from copy import deepcopy
from typing import Dict, List, Set, Sequence, Union, Optional
import json

SymbolType = str
AlphabetType = List[SymbolType]
StateNameType = str
TransistionsType = Dict[SymbolType, Set[StateNameType]]
StatesType = Dict[StateNameType, TransistionsType]


class NondeterministicFiniteAutomaton(object):
    _name: str
    _alphabet: AlphabetType
    _states: StatesType
    _start_state: StateNameType
    _accept_states: List[StateNameType]
    _is_epsilon: bool

    def __init__(self,
                 alphabet: AlphabetType = [],
                 start_state: StateNameType = "",
                 accept_states: List[StateNameType] = [],
                 states: StatesType = {},
                 name: str = ''):
        self._name = name
        self._alphabet = alphabet
        self._states = states
        self._start_state = start_state
        self._accept_states = accept_states
        self._is_epsilon = 'e' in alphabet

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def alphabet(self):
        return self._alphabet.copy()

    @property
    def states(self):
        return deepcopy(self._states)

    @property
    def start_state(self):
        return self._start_state

    @property
    def accept_states(self):
        return self._accept_states.copy()

    @property
    def is_epsilon(self):
        return self._is_epsilon

    def __len__(self):
        return len(self._states)

    def add_transistion(self,
                        state: StateNameType,
                        symbol: SymbolType,
                        dst_state: Union[StateNameType, Sequence[StateNameType]]):
        _dst_state = set([dst_state]) if isinstance(
            dst_state, StateNameType) else set(dst_state)
        new_states = _dst_state - self._states.keys()
        if len(new_states):
            self._states.update({a: {} for a in new_states})

        if self._states.get(state):
            if self._states[state].get(symbol):
                self._states[state][symbol].update(_dst_state)
            else:
                self._states[state][symbol] = _dst_state
        else:
            self._states[state] = {symbol: _dst_state}

        if symbol == 'e':
            self._is_epsilon = True

    def e_close(self, state: Optional[StateNameType] = None) -> Union[Set[StateNameType], Dict[StateNameType, Set[StateNameType]]]:
        """ Возвращает
        - tuple[StateNameType] - ε-замыкание для state, если он передан
        - Dict[StateNameType, tuple[StateNameType]] - ε-замыкание для всех состояний автомата если state не передан
        """
        def _e_close(e_state):
            result: Set[StateNameType] = set()
            result.add(e_state)
            Q = set()
            Q.add(e_state)
            while Q:
                c_state = Q.pop()
                t = self._states[c_state].get('e', set())
                result.update(t)
                Q.update(t)
            return tuple(result)

        if state and len(state):
            return _e_close(state)

        result: Dict[StateNameType, Set[StateNameType]] = {}
        for _state in self.states:
            result[_state] = _e_close(_state)
        return result

    def print(self):
        max_len_state_name = max(len(x) for x in self._states.keys())
        max_len_symbol = max(len(x) for x in self._alphabet)

        if self._name and len(self._name):
            print("NFA:  %s" % self._name)
        print("Alphabet:", ', '.join(self._alphabet))
        print("isEpsilon: %s" % ('✓' if self._is_epsilon else '✕'))
        print("States:")
        for state, transistions in self._states.items():
            prefix_name = ''
            if state in self.accept_states: prefix_name = '*'
            if state == self.start_state: prefix_name += '->'
            print("%s%s%s:" % (' ' * (max_len_state_name - len(state) -
                  len(prefix_name) + 4), prefix_name, state))
            for symbol, dst_states in transistions.items():
                print("%s%s: %s" % (
                    ' ' * (max_len_state_name +
                           max_len_symbol - len(symbol) + 5),
                    symbol,
                    ', '.join(dst_states)))

        print("Accept states:", ', '.join(self._accept_states))
        print("Start state:", self._start_state)

    # def to_automatonsimulator_format(self):
    #     states = self.states
    #     for (state_name, transistions) in states.items():
    #         for (symbol, dest_states) in transistions.items():
    #             states[state_name][symbol] = list(dest_states)
    #     obj = {
    #         "type": "NFA",
    #         'nfa': {
    #             'acceptStates': self.accept_states,
    #             'startState': self.start_state,
    #             'transitions': states
    #         },
    #         "states": {x: {} for x in self.states},
    #         "transitions": [
    #         {
    #             "stateA": stateA,
    #             "label": symbol,
    #             "stateB": stateB
    #         } for (stateA, transistion) in states.items() for (symbol, dest_states) in transistion.items() for stateB in dest_states],
    #         "bulkTests": {"accept": "", "reject": ""},
    #     }
    #     return json.dumps(obj)

NFA = NondeterministicFiniteAutomaton
