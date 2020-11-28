from typing import Optional
from NondeterministicFiniteStateMachine import NFA
from DeterministicFiniteStateMachine import DFA


def nfa_from_file(file_path: str, name: Optional[str] = None):
    def parse_str_state(str: str):
        transistions = {}
        (state, str_transistions) = str.strip().split("=")
        str_transistions = str_transistions[1:-2].split("],")
        for i in str_transistions:
            (symbol, str_states) = i.split(":[")
            tmp = str_states.split(",")
            if len(tmp[0]):
                transistions.update({symbol: tmp})
        return (state, transistions)
        
    nfa = NFA(name=name)
    with open(file_path, 'r') as file:
        size = int(file.readline())
        nfa._alphabet = [symbol.strip() for symbol in file.readline().strip()[
            1:-1].split(",")]
        for _ in range(size):
            (state, transistions) = parse_str_state(file.readline())
            for symbol, states in transistions.items():
                nfa.add_transistion(state, symbol, states)
        nfa._start_state = file.readline().strip()
        nfa._accept_states = [state.strip() for state in file.readline().strip()[
            1:-1].split(",")]
    return nfa

def dfa_from_file(file_path: str, name: Optional[str] = None):
    dfa = DFA(name=name)
    with open(file_path, 'r') as file:
        size = int(file.readline())
        dfa._alphabet = [symbol.strip() for symbol in file.readline().strip()[
            1:-1].split(",")]
        for _ in range(size):
            (state, str_transistions) = file.readline().strip().split("=")
            transistions = dict([i.split(":") for i in str_transistions[1:-1].split(",")])
            for symbol, dst_state in transistions.items():
                dfa.add_transistion(state, symbol, dst_state)
        dfa._start_state = file.readline().strip()
        dfa._accept_states = [state.strip() for state in file.readline().strip()[
            1:-1].split(",")]
    return dfa
