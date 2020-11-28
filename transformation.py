from copy import deepcopy
from typing import Dict, List, Set, Sequence, Union, Optional

from NondeterministicFiniteStateMachine import NFA, StatesType as NfaStatesType
from DeterministicFiniteStateMachine import DFA, StatesType as DfaStatesType


def nfa_to_dfa(nfa: NFA) -> DFA:
    e_close = nfa.e_close()
    P = set()
    P.add(e_close[nfa.start_state])

    dfa = {}

    # dfa: Dict[tuple[StateNameType], Dict[SymbolType, Set[StateNameType]]]
    # dfa_dest: Dict[SymbolType, Set[StateNameType]]
    # dfa_state_list: tuple[StateNameType]
    # nfa_dest_list: Set[StateNameType]

    while P:
        dfa_state_list = P.pop()
        dfa_dest = {}

        for nfa_state in dfa_state_list:
            for symbol, nfa_dest_list in nfa.states[nfa_state].items():
                if symbol != 'e':
                    dfa_dest.setdefault(symbol, set())
                    for st in nfa_dest_list:
                        dfa_dest[symbol].update(e_close[st])

        dfa[dfa_state_list] = dfa_dest

        keys = dfa.keys()
        for _, state in dfa_dest.items():
            if tuple(state) not in keys:
                P.add(tuple(state))

    init_accept_states = [''.join(state) for state in dfa if set(
        nfa.accept_states) & set(state)]

    init_alphabet = nfa.alphabet
    if 'e' in init_alphabet:
        init_alphabet.remove('e')
    init_alphabet.sort()

    init_dfa = {}
    while len(dfa):
        (state_name, state_data) = dfa.popitem()
        init_dfa[''.join(state_name)] = {symbol: ''.join(
            state) for (symbol, state) in state_data.items()}

    return DFA(
        alphabet=init_alphabet,
        start_state=''.join(e_close[nfa.start_state]),
        accept_states=init_accept_states,
        states=init_dfa,
        name=nfa.name
    )


def regex_str_to_nfa(reg: str, name: str = ''):
    _action_symbolls = ['+', '.', '(', ')', '*']
    init_alphabet: Set[str] = set('e')

    states: NfaStatesType = {
        'q0': {},
        'qf': {},
    }

    count = 0

    def get_new_state():
        nonlocal count
        count += 1
        return 'q' + str(count)

    def add_transistion(state, symbol, dest_states):
        nonlocal states
        if isinstance(dest_states, str):
            dest_states = {dest_states}
        if states.get(state):
            if states[state].get(symbol):
                states[state][symbol].update(dest_states)
            else:
                states[state][symbol] = dest_states
        else:
            states[state] = {symbol: dest_states}

    def parse_expr(r: str, start: str, end: str):
        current_state: str = start
        or_end_states: List[str] = []
        prev_is_simbol = False

        def or_end(end_state: str):
            nonlocal or_end_states
            if len(or_end_states):
                for state in or_end_states:
                    add_transistion(state, 'e', end_state)
                or_end_states = []

        i = 0
        while i < len(r):
            save_prev_is_simbol = False
            if r[i] in _action_symbolls:
                if r[i] == ')':
                    raise ValueError(
                        "Плохая регулярка - не скобочное выражение (1)")
                elif r[i] == '(':
                    start_index = i
                    brackets_num = 1
                    while brackets_num:
                        i += 1
                        if not i < len(r):
                            raise ValueError(
                                "Плохая регулярка - не скобочное выражение (2)")
                        if r[i] == '(':
                            brackets_num += 1
                        elif r[i] == ')':
                            brackets_num -= 1
                    end_index = i
                    i += 1
                    if i < len(r) and r[i] == '*':
                        st1 = get_new_state()  # + '(prev)'
                        add_transistion(current_state, 'e', st1)
                        left_state = get_new_state()  # + '(left)'
                        right_state = get_new_state()  # + '(right)'
                        current_state = get_new_state()  # + '(curr)'
                        add_transistion(st1, 'e', [left_state, current_state])
                        add_transistion(right_state, 'e', [
                                        left_state, current_state])
                        parse_expr(r[start_index+1:end_index],
                                   left_state, right_state)
                        i += 1
                    else:
                        left_state = get_new_state()
                        add_transistion(current_state, 'e', left_state)
                        current_state = get_new_state()
                        parse_expr(r[start_index+1:end_index],
                                   left_state, current_state)
                elif r[i] == '+':
                    or_end_states.append(current_state)
                    current_state = start
                    i += 1
                elif r[i] == '*':
                    raise ValueError("Что-то пошло не так")
                elif r[i] == '.':
                    save_prev_is_simbol = True
                    i += 1
                if not save_prev_is_simbol:
                    prev_is_simbol = False
            else:
                init_alphabet.add(r[i])
                if not (i+1 < len(r) and r[i+1] == '*'):
                    prev_state = current_state
                    if not prev_is_simbol:
                        prev_state = get_new_state()
                        add_transistion(current_state, 'e', prev_state)
                    current_state = get_new_state()
                    add_transistion(prev_state, r[i], current_state)
                    prev_is_simbol = True
                    i += 1
                else:
                    st1 = get_new_state()  # + '(st1)'
                    add_transistion(current_state, 'e', st1)
                    st2 = get_new_state()  # + '(st2)'
                    st3 = get_new_state()  # + '(st3)'
                    current_state = get_new_state()  # + '(st4)'
                    add_transistion(st1, 'e', [st2, current_state])
                    add_transistion(st2, r[i], st3)
                    add_transistion(st3, 'e', st2)
                    add_transistion(st3, 'e', current_state)
                    i += 2

        if len(or_end_states):
            or_end_states.append(current_state)
            or_end(end)
        else:
            add_transistion(current_state, 'e', end)

    parse_expr(reg, 'q0', 'qf')

    return NFA(
        alphabet=list(init_alphabet),
        start_state='q0',
        accept_states=['qf'],
        states=states,
        name=name
    )


def dfa_to_regex(dfa: DFA) -> str:
    PARENTS = 1
    # PARENTS = 'PARENTS'
    states = dfa.states
    
    def transistion_formating(R, postfix = ''):
        if isinstance(R, str):
            return '(%s)%s' % (R, postfix) if len(R) > 1 else '%s%s' % (R, postfix)
        if len(R) > 1:
            return '(%s)%s' % ('+'.join(R), postfix)
        R = ''.join(R)
        if len(R) > 1:
            return '(%s)%s' % (R, postfix)
        return '%s%s' % (R, postfix)

    def del_brackets(in_str):
        i = 0
        while i < len(in_str):
            plus = False
            if in_str[i] == '(':
                j = i
                n = 1
                while n > 0 and j < len(in_str):
                    j += 1
                    if in_str[j] == '(':
                        n += 1
                    elif in_str[j] == ')':
                        n -= 1
                    elif n == 1 and in_str[j] == '+':
                        plus = True

                left_close = False
                right_close = False

                if plus and i - 1 >= 0 and in_str[i - 1] not in ('(', '+'):
                    left_close = True
                if plus and j + 1 < len(in_str) and in_str[j + 1] not in (')', '+'):
                    right_close = True

                if not (j + 1 < len(in_str) and in_str[j+1] == '*') and not (left_close or right_close):
                    in_str = in_str[:i] + in_str[i+1:j] + in_str[j+1:]
                    i -= 1
            i += 1
        return in_str

    for (state, transistions) in dfa.states.items():
        for (symbol, dst_state) in transistions.items():
            if states[dst_state].get(PARENTS):
                if states[dst_state][PARENTS].get(state):
                    states[dst_state][PARENTS][state].add(symbol)
                else:
                    states[dst_state][PARENTS][state] = {symbol}
            else:
                states[dst_state][PARENTS] = {state: {symbol}}

    for state in states:
        if states[state].get(PARENTS):
            for parent in states[state][PARENTS]:
                states[state][PARENTS][parent] = tuple(states[state][PARENTS][parent])

    chains = []

    for accept_state in dfa.accept_states:
        tmp_states = deepcopy(states)
        for state in states:
            if state != dfa.start_state and state != accept_state:
                loop = tmp_states[state][PARENTS].get(state, '')
                if loop:
                    loop = transistion_formating(loop, '*')
                del_parents = set()
                for (parent, parent_symbols) in tmp_states[state][PARENTS].items():
                    if parent != state:
                        for (dst_symbol, dst) in tmp_states[state].items():
                            if dst_symbol != PARENTS and dst != state:
                                old_symbols = tmp_states[dst][PARENTS].get(parent, '')
                                for old_symbol in old_symbols:
                                    tmp_states[parent].pop(old_symbol, '')
                                if old_symbols:
                                    old_symbols = transistion_formating(old_symbols, '+')

                                left = transistion_formating(parent_symbols)
                                right = transistion_formating(dst_symbol)

                                sym = '%s%s%s%s' % (
                                    old_symbols,
                                    left,
                                    loop,
                                    right
                                )
                                tmp_states[parent][sym] = dst
                                tmp_states[dst][PARENTS][parent] = tuple({sym})
                                del_parents.add(dst)
                        for parent_symbol in parent_symbols:
                            tmp_states[parent].pop(parent_symbol, '')
                for dst in del_parents:
                    tmp_states[dst][PARENTS].pop(state, '')
                tmp_states.pop(state)

        if len(tmp_states) == 2:
            R = tmp_states[dfa.start_state][PARENTS].get(dfa.start_state, '')
            if R:
                R = transistion_formating(R, '+')
            S = transistion_formating(tmp_states[accept_state][PARENTS][dfa.start_state])
            U = tmp_states[accept_state][PARENTS].get(accept_state, '')
            T = transistion_formating(tmp_states[dfa.start_state][PARENTS][accept_state], '')
            if U:
                U = transistion_formating(U, '*')
            chains.append('(%s%s%s%s)*%s%s' % (R, S, U, T, S, U))
        elif len(tmp_states) == 1:
            chains.append("(%s)*" % ''.join(tmp_states[dfa.start_state][PARENTS].get(dfa.start_state, '')))

    if len(chains) == 1:
        return del_brackets('%s' % chains[0])
    return del_brackets('(%s)' % ')+('.join(chains))
