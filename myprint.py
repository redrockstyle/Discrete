def print_e_close(e_close):
    if not e_close:
        print("Нет ε-переходов")
        return
    for state, e_states in e_close.items():
        print("  %s:  %s" % (state, ', '.join(e_states)))