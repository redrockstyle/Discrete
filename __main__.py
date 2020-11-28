import sys

from NondeterministicFiniteStateMachine import NFA
from DeterministicFiniteStateMachine import DFA
from parse import *
from transformation import nfa_to_dfa, regex_str_to_nfa, dfa_to_regex
from myprint import *

PATH_PREFIX = "./lab"
FILE_PREFIX = "test"
FILE_POSTFIX = ".txt"
SEPARATOR = "-" * 30
SEPARATOR_B = "=" * 30
SEPARATOR_L = '.' * 30

if __name__ == "__main__":
    def do_lab1(n_test):
        file_path = PATH_PREFIX + '1' + "/" + FILE_PREFIX + n_test + FILE_POSTFIX
        nfa = nfa_from_file(file_path, "LAB_1 TEST_%s\n" % (n_test))

        nfa.print()
        if nfa.is_epsilon:
            print(SEPARATOR_L)
            print("ε_close:")
            print_e_close(nfa.e_close())

        print(SEPARATOR * 2)
        dfa = nfa_to_dfa(nfa)
        dfa.print()

    def do_lab2(n_test):
        tests = {
            '1': '00(0+1)*',
            '2': '(0+101)*1*',
            '3': '(01+10)*(1+010)',
            '4': '0*(1+01)(11+0*)*',
            '5': '((0+1*)+(11+010+0*))*',
        }

        exp = tests.get(n_test)
        if exp:
            name = 'LAB_2 TEST_%s' % (n_test)
            print('EXP %s' % name)
            print(exp)
            print(SEPARATOR_L * 2)
            nfa = regex_str_to_nfa(exp, name)
            nfa.print()
        else:
            name = 'LAB_2 CE'
            print(name)
            print(n_test)
            print(SEPARATOR_L * 2)
            nfa = regex_str_to_nfa(n_test, name)
            nfa.print()

    def do_lab3(n_test):
        file_path = PATH_PREFIX + '3' + "/" + FILE_PREFIX + n_test + FILE_POSTFIX
        dfa = dfa_from_file(file_path, "LAB_3 TEST_%s\n" % n_test)
        dfa.print()
        print(SEPARATOR * 2)
        reg = dfa_to_regex(dfa)
        print(reg)

    def do_lab4(n_test):
        file_path = PATH_PREFIX + '4' + "/" + FILE_PREFIX + n_test + FILE_POSTFIX
        dfa = dfa_from_file(file_path, "LAB_4 TEST_%s\n" % n_test)
        dfa.print()
        print(SEPARATOR * 2)
        dfa.minimization()
        print(SEPARATOR * 2)
        dfa.print()

    def do_mega_lab(n_test):
        file_path = PATH_PREFIX + '4' + "/" + FILE_PREFIX + n_test + FILE_POSTFIX
        dfa = dfa_from_file(file_path, "MEGA_LAB TEST_%s\n" % n_test)

        print('Вход:')
        dfa.print()
        print()

        print(SEPARATOR)
        print('Минимизированный:')
        dfa.minimization()
        dfa.print()

        # print(SEPARATOR)
        # print('Преобразование в регулярку:')
        reg = dfa_to_regex(dfa)
        # print(reg)

        # print(SEPARATOR)
        # print('Преобразование регулярки в nfa:')
        nfa = regex_str_to_nfa(reg, dfa.name)
        # nfa.print()

        # print(SEPARATOR)
        # print('Преобразование nfa в dfa (dfa2):')
        dfa2 = nfa_to_dfa(nfa)
        # dfa2.rename_states()
        # dfa2.print()

        print(SEPARATOR)
        print('Минимизация dfa2:')
        dfa2.minimization()
        dfa2.rename_states()
        dfa2.print()


    labs = {
        '1': do_lab1,
        '2': do_lab2,
        '3': do_lab3,
        '4': do_lab4,
        '5': do_mega_lab,
    }

    if len(sys.argv) < 3:
        raise ValueError("Укажите номер лабы и теста")

    n_lab = sys.argv[1]
    if n_lab not in labs:
        raise ValueError("Нет такой лабы")
    
    n_test = sys.argv[2]

    print(SEPARATOR_B * 3)
    print(SEPARATOR_B * 3)
    labs[n_lab](n_test)
    print(SEPARATOR_B * 3)
    print(SEPARATOR_B * 3)
