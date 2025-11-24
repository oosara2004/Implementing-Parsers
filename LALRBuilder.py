from collections import defaultdict, deque
from SimpleLR1Builder import LR1

# LALR Converter

def build_LALR(C, ACTION, GOTO):
    groups = defaultdict(list)

    def get_kernel(I):
        return frozenset({ (it.left, tuple(it.right), it.dot)
                           for it in I
                           if not (it.dot == 0 and it.left != "S'") })

    for i, I in enumerate(C):
        groups[get_kernel(I)].append(i)

    merged_states = {}
    new_index = {}
    counter = 0

    for kernel, lst in groups.items():
        merged_states[counter] = set()
        for old in lst:
            merged_states[counter] |= C[old]
        for old in lst:
            new_index[old] = counter
        counter += 1

    LALR_ACTION = defaultdict(dict)
    LALR_GOTO = defaultdict(dict)

    for old in new_index:
        new = new_index[old]
        for a, act in ACTION[old].items():
            if a in LALR_ACTION[new] and LALR_ACTION[new][a] != act:
                print("ACTION conflict, grammar is NOT LALR!")
                return None, None, None
            LALR_ACTION[new][a] = act
        for A, go in GOTO[old].items():
            LALR_GOTO[new][A] = new_index[go]

    return merged_states, LALR_ACTION, LALR_GOTO


def print_LALR(States, ACTION, GOTO):
    print(" LALR States ")
    for i, items in States.items():
        print(f"State {i}:")
        for it in items:
            # NOTE: Replacing epsilon (ε) with empty string 
            item_str = str(it).replace("ε", "")
            print("  ", item_str)
        print()

    print("LALR ACTION Table")
    terminals = sorted({t for row in ACTION.values() for t in row})
    print("    ", " ".join(f"{t:>6}" for t in terminals))
    for s in States:
        row = [ACTION[s].get(t, "") for t in terminals]
        print(f"{s:<3}", " ".join(f"{v:>6}" for v in row))

    print("\n LALR GOTO Table ")
    nonterms = sorted({A for row in GOTO.values() for A in row})
    print("    ", " ".join(f"{nt:>6}" for nt in nonterms))
    for s in States:
        row = [GOTO[s].get(A, "") for A in nonterms]
        print(f"{s:<3}", " ".join(f"{v:>6}" for v in row))


# Main

if __name__ == "__main__":
    # 1) Build canonical LR(1)
    b = LR1("G1") 
    C, ACTION, GOTO = b.build()

    # 2) Convert to LALR
    States, LA, LG = build_LALR(C, ACTION, GOTO)

    if States is not None:
        print_LALR(States, LA, LG)
    else:
        print("Grammar is not LALR!")
