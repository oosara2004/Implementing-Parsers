from collections import defaultdict, deque
from SimpleLR1Builder import LR1

def item_to_str(it):
    # replace epsilon with empty string
    return str(it).replace("ε", "eps")

def build_LALR(C, ACTION, GOTO):
    """
    Build LALR by merging LR(1) states with identical kernels.
    IMPORTANT FIX: remap shift targets (sN) to new merged indices,
    otherwise shift actions from different old states look different
    and produce false conflicts.
    """
    groups = defaultdict(list)

    def get_kernel(I):
        return frozenset({ (it.left, tuple(it.right), it.dot)
                           for it in I
                           if not (it.dot == 0 and it.left != "S'") })

    for i, I in enumerate(C):
        groups[get_kernel(I)].append(i)

    merged_states = {}
    old_to_new = {}
    counter = 0
    for kernel, old_list in groups.items():
        merged = set()
        for old in old_list:
            merged |= C[old]
        merged_states[counter] = merged
        for old in old_list:
            old_to_new[old] = counter
        counter += 1

    LALR_ACTION = defaultdict(dict)
    LALR_GOTO = defaultdict(dict)

    new_to_old = defaultdict(list)
    for old, new in old_to_new.items():
        new_to_old[new].append(old)

    for old in sorted(old_to_new.keys()):
        new = old_to_new[old]

       
        for a, act in ACTION[old].items():
           
            if isinstance(act, str) and act.startswith("s"):
                
                try:
                    old_target = int(act[1:])
                except:
                    
                    remapped = act
                else:
                    if old_target not in old_to_new:
                       
                        remapped = f"s{old_target}"
                    else:
                        remapped = f"s{old_to_new[old_target]}"
            else:
                
                remapped = act

           
            if a in LALR_ACTION[new] and LALR_ACTION[new][a] != remapped:
                
                print("\nGrammar is NOT LALR (conflict during merging).")
                print(f"  Merged state {new} (old states {sorted(new_to_old[new])})")
                print(f"  Conflict on terminal '{a}': existing={LALR_ACTION[new][a]}  new={remapped}")
                return None, None, None

            LALR_ACTION[new][a] = remapped

        # Copy GOTO, remapping target indices to new merged indices
        for A, go in GOTO[old].items():
            if go not in old_to_new:
               
                LALR_GOTO[new][A] = go
            else:
                LALR_GOTO[new][A] = old_to_new[go]

    return merged_states, LALR_ACTION, LALR_GOTO

def print_LALR(States, ACTION, GOTO):
    print(" LALR States ")
    for i, items in sorted(States.items()):
        print(f"State {i}:")
        for it in sorted(items, key=lambda x:(x.left, tuple(x.right), x.dot, x.la)):
            print("  ", item_to_str(it))
        print()

    print(" LALR ACTION Table ")
    # collect terminals (make sure $ present)
    terminals = sorted({t for row in ACTION.values() for t in row})
    if "$" not in terminals:
        terminals.append("$")
    print("    ", " ".join(f"{t:>6}" for t in terminals))
    for s in sorted(States.keys()):
        row = [ACTION[s].get(t, "") for t in terminals]
        print(f"{s:<3}", " ".join(f"{v:>6}" for v in row))

    print("\n LALR GOTO Table ")
    nonterms = sorted({A for row in GOTO.values() for A in row})
    print("    ", " ".join(f"{nt:>6}" for nt in nonterms))
    for s in sorted(States.keys()):
        row = [GOTO[s].get(A, "") for A in nonterms]
        print(f"{s:<3}", " ".join(f"{v:>6}" for v in row))

if __name__ == "__main__":
   
    b = LR1("G2")
    C, ACTION, GOTO = b.build()

    States, LA, LG = build_LALR(C, ACTION, GOTO)

    if States is not None:
        print_LALR(States, LA, LG)
    else:
        print("Grammar is not LALR!")
