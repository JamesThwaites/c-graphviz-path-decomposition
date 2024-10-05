# from time import perf_counter
from dataclasses import dataclass

def get_entry_node(block: str) -> str:
    match block[0]:
        case 'i':
            return f"i{block[1:]}"
        
        case 'w':
            return f"w{block[1:]}"
        
        case 'o':
            return block
    
    return ''
        
def get_exit_node(block: str) -> str:
    match block[0]:
        case 'p':
            return 'p'
        
        case 'f':
            return f"f{block[1:]}"
        
        case 'd':
            return f"d{block[1:]}"
        
        case 'o':
            return block
        
    return ''

@dataclass
class NiceTriple:
    vertex: str
    delta: int
    cumulative_weight: int

    def __repr__(self):
        return f"{self.vertex},{self.delta},{self.cumulative_weight}"

def nice_decompose(program: list[str]) -> list[NiceTriple]:
    cumulative_weight = 0
    decomp: list[NiceTriple] = []
    decomp.append(NiceTriple("p", 1, cumulative_weight))
    cumulative_weight += 1
    # start = perf_counter()

    for i, node in enumerate(program):
        tail = node[1:]

        if i == 1:
            cumulative_weight += 1
            decomp.append(NiceTriple("m", 1, cumulative_weight))

        match node[0]:
            case 'i':
                if get_exit_node(program[i-1]) == '':
                    cumulative_weight += 1
                    decomp.append(NiceTriple(f"i{tail}", 1, cumulative_weight))

                cumulative_weight += 1
                decomp.append(NiceTriple(f"f{tail}", 1, cumulative_weight))
            
            case 'f':
                cumulative_weight -= 1
                decomp.append(NiceTriple(f"f{tail}", -1, cumulative_weight))

                if get_entry_node(program[i+1]) == '':
                    cumulative_weight -= 1
                    decomp.append(NiceTriple(f"f{tail}", -1, cumulative_weight))

            case 'w':
                if get_exit_node(program[i-1]) == '':
                    cumulative_weight += 1
                    decomp.append(NiceTriple(f"w{tail}", 1, cumulative_weight))
                
                cumulative_weight += 1
                decomp.append(NiceTriple(f"d{tail}", 1, cumulative_weight))

            case 'd':
                cumulative_weight -= 1
                decomp.append(NiceTriple(f"w{tail}", -1, cumulative_weight))

                if get_entry_node(program[i+1]) == '':
                    cumulative_weight -= 1
                    decomp.append(NiceTriple(f"d{tail}", -1, cumulative_weight))
            
            case 'o':
                if get_exit_node(program[i - 1]) == '':
                    cumulative_weight += 1
                    decomp.append(NiceTriple(node, 1, cumulative_weight))

                if get_entry_node(program[i+1]) == '':
                    cumulative_weight -= 1
                    decomp.append(NiceTriple(node, -1, cumulative_weight))
            
            case 'm':
                cumulative_weight -= 1
                decomp.append(NiceTriple("m", -1, cumulative_weight))
                continue

        if i < len(program):
            exit_half = get_exit_node(node)
            entry_half = get_entry_node(program[i + 1])
            if entry_half != '' and exit_half != '':
                cumulative_weight += 1
                decomp.append(NiceTriple(entry_half, 1, cumulative_weight))
                cumulative_weight -= 1
                decomp.append(NiceTriple(exit_half, -1, cumulative_weight))

    return decomp

if __name__ == '__main__':
    program = input().split(' ')
    print(program)

    for bag in nice_decompose(program):
        print(bag)

    # print(perf_counter() - start)