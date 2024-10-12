# from time import perf_counter

def get_entry_node(block: str) -> str:
    match block[0]:
        case 'i':
            return f"if_{block[1:]}"
        
        case 'w':
            return f"while_{block[1:]}"
        
        case 'o':
            return block
    
    return ''
        
def get_exit_node(block: str) -> str:
    match block[0]:
        case 'p':
            return 'program'
        
        case 'f':
            return f"fi_{block[1:]}"
        
        case 'd':
            return f"done_{block[1:]}"
        
        case 'o':
            return block
        
    return ''

program = input().split(' ')

def decompose(program: list[str]) -> list[set[str]]:
    decomp = list()
    include = set()
    # start = perf_counter()

    for i, node in enumerate(program):
        tail = node[1:]

        if i == 1:
            include.add("margorp")

        match node[0]:
            case 'i':
                include.add(f"if_{tail}")
                include.add(f"fi_{tail}")
            
            case 'f':
                include.remove(f"if_{tail}")
                include.remove(f"fi_{tail}")

            case 'w':
                include.add(f"while_{tail}")
                include.add(f"done_{tail}")

            case 'd':
                include.remove(f"while_{tail}")
                include.remove(f"done_{tail}")
            
            case 'o':
                decomp.append( include | set((node,)) )
            
            case 'm':
                continue

        if i < len(program):
            exit_half = get_exit_node(node)
            entry_half = get_entry_node(program[i + 1])
            if entry_half != '' and exit_half != '':
                decomp.append( set((exit_half, entry_half)) | include )

    return decomp



# print(program)

for bag in decompose(program):
    print(bag)

# print(perf_counter() - start)