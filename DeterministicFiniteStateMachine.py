from copy import deepcopy
from typing import Dict, List, Set, Sequence, Union

SymbolType = str
AlphabetType = List[SymbolType]
StateNameType = str
StatesType = Dict[StateNameType, Dict[SymbolType, StateNameType]]

class DeterministicFiniteAutomaton(object):
    _name: str
    _alphabet: AlphabetType
    _states: StatesType
    _start_state: StateNameType
    _accept_states: List[StateNameType]

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

    @property
    def name(self):
        return self._name

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

    def __len__(self):
        return len(self._states)

    def add_transistion(self,
                        state: StateNameType,
                        symbol: SymbolType,
                        dst_state: StateNameType):
        if dst_state not in self._states: self._states[dst_state] = {}
        if self._states.get(state):
            self._states[state][symbol] = dst_state
        else:
            self._states[state] = {symbol: dst_state}

    def minimization(self):
        """ Возвращает -1 если автомат уже оптимизирован """
        # × = False   _ = True
        states = sorted(self._states.keys())
        table = {}

        def print_tables(active_state=False, symbol=False):
            max_len = max(len(x) for x in states)
            left_separator = '  '
            box_size = max_len + 1
            def bool_to_symbol(b):
                return '-' if b else '×'

            print(' ' * (max_len + 3), '0'.center(max_len + 1), '1'.center(max_len + 1))

            for i, s in enumerate(states):
                if i + 1 < len(states):
                    left = states[i + 1]
                else:
                    left = False
                automata_str = '%s |  %s %s' % (s.rjust(max_len), self._states[s]['0'].center(max_len + 1), self._states[s]['1'].center(max_len + 1))
                if active_state and active_state == s:
                    automata_str += ' <'
                    if symbol:
                        automata_str += ' %s' % symbol
                if left:
                    table_str = '%s%s' % (left.rjust(max_len), left_separator)
                    for bot in states[:i+1]:
                        # print('bot =', bot, ' left =', left)
                        table_str += bool_to_symbol(table[bot][left]).center(box_size)
                else:
                    table_str = '%s%s' % (' ' * max_len, ' ' * len(left_separator))
                    for bot in states[:-1]:
                        table_str += bot.center(box_size)
                automata_container_size = 3*max_len + 6
                if active_state: automata_container_size += 2
                if symbol: automata_container_size += 1 + len(symbol)
                print('%s%s' % (automata_str.ljust(automata_container_size + 6), table_str))
            print()
        
        # начальные значения таблички
        for i, bot in enumerate(states[:-1]):
            bot_is_accept = bot in self._accept_states
            for left in states[i+1:]:
                istinguishable = bot_is_accept == (left in self._accept_states)
                if table.get(bot):
                    table[bot][left] = istinguishable
                else:
                    table[bot] = {left: istinguishable}

        
        # print('=' * 40)
        # print('Начало')
        # print_tables()
        # print('-' * 30)


        # Ходим по табличке
        already_minimized = True
        change_flag = True
        while(change_flag):
            change_flag = False
            already_minimized = True

            # print('\n', '=' * 15, 'Итерация', j, '=' * 15)
            
            for i, bot in enumerate(states[:-1]):
                for left in states[i+1:]:
                    if table[bot][left]:

                        # print()
                        # print('-' * 26)
                        # print(f'Смотрим {bot}:{left}')

                        already_minimized = False
                        for s in self._alphabet:
                            tr_bot, tr_left = sorted((self._states[bot][s], self._states[left][s]))
                            
                            # print(f'  По {s} - {tr_bot}:{tr_left}', end='')

                            if tr_bot != tr_left and not table[tr_bot][tr_left]:
                                change_flag = True
                                # print(f' = {table[tr_bot][tr_left]}')
                                # print(f'    Ставим × на {bot}:{left}')
                                table[bot][left] = False # ставим ×
                                break

                            # elif tr_bot == tr_left:
                            #     print(' равны ' + self._states[tr_bot][s])
                            # else:
                            #     print()

        if already_minimized:
            # print('\nУЖЕ ОПТИМИЗИРОВАН\n')
            return -1

        # print()
        # print('-' * 30)
        # print('Финал')
        # print_tables()
        # print('.' * 30)

        # Собираем новые состояния
        new_states: StatesType = {}
        new_start_state = self._start_state
        new_accept_states: List[StateNameType] = []

        used_states = []
        tmp_map_name_states = {}

        for i, bot in enumerate(states[:-1]):
            if bot not in used_states:
                new_state = []
                new_state.append(bot)

                for left in states[i+1:]:
                    if table[bot][left]:
                        new_state.append(left)
                used_states += new_state

                name_new_state = ''.join(new_state)
                new_states[name_new_state] = {}

                if self._start_state in new_state:
                    new_start_state = name_new_state

                if set(new_state) & set(self._accept_states):
                    new_accept_states.append(name_new_state)

                for st in new_state:
                    tmp_map_name_states[st] = name_new_state
        if (states[-1] not in used_states) and len(states) > 1 and not table[states[-2]][states[-1]]:
            new_states[states[-1]] = {}
            tmp_map_name_states[states[-1]] = states[-1]

        for state in self._states:
            for symbol in self._alphabet:
                new_states[tmp_map_name_states[state]][symbol] = tmp_map_name_states[self._states[state][symbol]]

        self._start_state = new_start_state
        self._accept_states = new_accept_states
        self._states = new_states

    def rename_states(self):
        count = 1
        new_states = {}
        new_accept_states = []
        new_names_states = {self._start_state: 'q0', 'ø': 'ø'}
        for state in self._states:
            if state not in (self._start_state, 'ø'):
                new_names_states[state] = 'q' + str(count)
                count += 1
        for st in self._accept_states:
            new_accept_states.append(new_names_states[st])
        for state in self._states:
            new_states[new_names_states[state]] = {}
            for symbol in self._states[state]:
                new_states[new_names_states[state]][symbol] = new_names_states[self._states[state][symbol]]
        self._states = new_states
        self._accept_states = new_accept_states
        self._start_state = 'q0'
            


    def print(self):
        max_len_state_name = max(len(x) for x in self._states.keys())
        max_len_symbol = max(len(x) for x in self._alphabet)
        dest_container_size = max(max_len_state_name, max_len_symbol) + 2
        empty_state_flag = False

        if self._name and len(self._name):
            print("DFA:  %s" % self._name)
        print("Alphabet:", ', '.join(self._alphabet))
        print("States:")
        symbols_str = ''
        for symbol in self._alphabet:
            symbols_str += symbol.center(dest_container_size)
        print('%s   %s' % (' ' * (max_len_state_name + 3), symbols_str))
        for state, transistion in self._states.items():
            prefix_name = ''
            if state in self.accept_states:
                prefix_name = '*'
            if state == self.start_state:
                prefix_name += '->'
            name_str = "%s%s%s" % (
                ' ' * (max_len_state_name - len(state) - len(prefix_name) + 3),
                prefix_name,
                state
            )
            transistions_str = ''
            for symbol in self._alphabet:
                dest = transistion.get(symbol, 'ø')
                if dest == 'ø': empty_state_flag = True
                transistions_str += dest.center(dest_container_size)
            print('%s | %s' % (name_str, transistions_str))
        if empty_state_flag:
            name_str = "%sø" % (' ' * (max_len_state_name + 2))
            transistions_str = ''
            for symbol in self._alphabet:
                transistions_str += 'ø'.center(dest_container_size)
            print('%s | %s' % (name_str, transistions_str))

        print("Accept states:", ', '.join(self._accept_states))
        print("Start state:", self._start_state)


DFA = DeterministicFiniteAutomaton
