# FOR COMPUTING NICE DECOMP #
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


# FOR COMPUTING EXACT DECOMP #
from collections import OrderedDict
from dataclasses import dataclass

@dataclass
class Skeleton:
    skeleton: list[NiceTriple]
    members: set[str]
    width: int

    def __str__(self):
        return f"{' '.join([node.vertex for node in self.skeleton])}"

def build_neighbours(program: list[str]):
    def forward(block: str, i: int, program: list[str]):
        match block[0]:
            case 'e':
                # return forward(program[i + 1], i + 1, program)
                return f"f{block[1:]}"
            
            case 'b':
                return f"d{block[1:]}"
            
            case 'c':
                return f"w{block[1:]}"
            
            case _:
                return block
            
    def backward(block: str, i: int, program: list[str]):
        match block[0]:
            case 'e':
                return f"i{block[1:]}"
            
            case 'b':
                return backward(program[i - 1], i - 1, program)
            
            case 'c':
                return backward(program[i - 1], i - 1, program)
            
            case _:
                return block

    neighbours: dict[str, set[str]] = OrderedDict()
    if_has_else: list[bool] = []

    for _, node in enumerate(program):
        if node[0] not in ('e', 'b', 'c'):
            neighbours[node] = set()

    for i, node in enumerate(program):
        match node[0]:
            case 'i':
                if_has_else.append(False)

            case 'e':
                if_has_else[int(node[1:])] = True
                continue

            case 'f':
                if not if_has_else[int(node[1:])]:
                    neighbours[node].add(f"i{node[1:]}")
                    neighbours[f"i{node[1:]}"].add(node)

            case 'd':
                neighbours[node].add(f"w{node[1:]}")
                neighbours[node].add(forward(program[i + 1], i + 1, program))
                continue

            case 'b':
                neighbours[b := backward(program[i - 1], i - 1, program)].add(f"d{node[1:]}")
                neighbours[f"d{node[1:]}"].add(b)
                continue

            case 'c':
                neighbours[b := backward(program[i - 1], i - 1, program)].add(f"w{node[1:]}")
                neighbours[f"w{node[1:]}"].add(b)
                continue

            case 'w':
                neighbours[node].add(f"d{node[1:]}")
                neighbours[node].add(forward(program[i + 1], i + 1, program))
                neighbours[node].add(backward(program[i - 1], i - 1, program))

        if i > 0:
            neighbours[node].add(b := backward(program[i - 1], i - 1, program))
            neighbours[b].add(node) 

        if i < len(program) - 1:
            neighbours[node].add(f := forward(program[i + 1], i + 1, program))
            neighbours[f].add(node)

    return neighbours

def get_neighbours_up_to(index: int, if_has_else: list[bool], program: list[str]):
    def backward(block: str, i: int, program: list[str]):
        match block[0]:
            case 'e':
                return f"i{block[1:]}"
            
            case 'b':
                return backward(program[i - 1], i - 1, program)
            
            case 'c':
                return backward(program[i - 1], i - 1, program)
            
            case _:
                return block

    neighbours: list[str] = []

    for _, node in enumerate(program):
        if node[0] not in ('e', 'b', 'c'):
            neighbours[node] = set()

    for i, node in enumerate(program):
        match node[0]:
            case 'i':
                if_has_else.append(False)

            case 'e':
                if_has_else[int(node[1:])] = True
                continue

            case 'f':
                if not if_has_else[int(node[1:])]:
                    neighbours[node].add(f"i{node[1:]}")
                    neighbours[f"i{node[1:]}"].add(node)

            case 'd':
                neighbours.append(f"w{node[1:]}")
                continue

            # case 'b':
            #     neighbours[b := backward(program[i - 1], i - 1, program)].add(f"d{node[1:]}")
            #     neighbours[f"d{node[1:]}"].add(b)
            #     continue

            # case 'c':
            #     neighbours[b := backward(program[i - 1], i - 1, program)].add(f"w{node[1:]}")
            #     neighbours[f"w{node[1:]}"].add(b)
            #     continue

            # case 'w':
            #     neighbours.add(f"d{node[1:]}")

        if i > 0:
            neighbours.append(backward(program[i - 1], i - 1, program))

    return neighbours

# MAIN #
def main():
    from copy import deepcopy
    program = input().split(' ')

    # PRE-PROCESS #
    neighbours = build_neighbours(program)
    nice_decomp = nice_decompose(program)

    k = max([n.cumulative_weight for n in nice_decomp]) # k = approximate path-width
    print("Max width:", k)

    skeletons = [
        Skeleton([
            NiceTriple(
                nice_decomp[0].vertex, 1, 0
            ),
            NiceTriple(
                nice_decomp[0].vertex, -1, -1
            )
        ], {nice_decomp[0].vertex}, 0)
    ]

    for j, nice_decomp_node in enumerate(nice_decomp[1:4], start = 1):
        new_skeletons: list[Skeleton] = []
        print(f"Iteration: {j+1}, Current # of Skeletons: {len(skeletons)}") if skeletons else None
        if nice_decomp_node.delta == 1:
            #print(neighbours[nice_decomp_node.vertex])
            current_neighbours = neighbours[nice_decomp_node.vertex]
            for skeleton in skeletons:
                relevant_neighbours = skeleton.members.intersection(current_neighbours)
                skeleton.members.add(nice_decomp_node.vertex)
                introduced = 0
                forgotten = 0
                for i, node in enumerate(skeleton.skeleton):
                    if forgotten < len(relevant_neighbours) or len(relevant_neighbours) == 0:
                        # do new skel
                        new_skel = deepcopy(skeleton)
                        new_int = introduced
                        if i == 0:
                            weight = -1
                        else:
                            weight = skeleton.skeleton[i-1].cumulative_weight
                        # might need to do an append if i == len(skeleton.skeleton)
                        new_skel.skeleton.insert(i, NiceTriple(nice_decomp_node.vertex, 1, weight + 1))

                        for l, new_node in enumerate(new_skel.skeleton[i:], start = i):
                            if l != i:
                                new_node.cumulative_weight += 1

                            if new_node.cumulative_weight >= k:
                                break

                            if new_node.cumulative_weight > new_skel.width:
                                new_skel.width = new_node.cumulative_weight

                            if new_node.delta == 1 and new_node.vertex in relevant_neighbours:
                                new_int += 1

                            if new_int >= len(relevant_neighbours):
                                to_add_skel = deepcopy(new_skel)
                                to_add_skel.skeleton.insert(l + 1, NiceTriple(nice_decomp_node.vertex, -1, new_node.cumulative_weight - 1))
                                new_skeletons.append(to_add_skel)

                    if node.delta == 1 and node.vertex in relevant_neighbours:
                        introduced += 1

                    elif node.delta == -1 and node.vertex in relevant_neighbours:
                        forgotten += 1



        elif nice_decomp_node.delta == -1:
            for skeleton in skeletons:
                sk = skeleton.skeleton
                skeleton.members.remove(nice_decomp_node.vertex)
                convert_count = 0
                for i, node in enumerate(sk):
                    if node.vertex == nice_decomp_node.vertex:
                        node.vertex = '0'
                        convert_count += 1

                    if convert_count == 2:
                        break

                cursor = 0
                while cursor < len(sk):
                    if (
                        sk[cursor].vertex == '0' and
                        ((cursor == 0 or cursor == len(sk) - 1)
                        or (sk[cursor].cumulative_weight >= min(sk[cursor-1].cumulative_weight, sk[cursor+1].cumulative_weight)
                        and sk[cursor].cumulative_weight <= max(sk[cursor-1].cumulative_weight, sk[cursor+1].cumulative_weight)
                        ))
                    ):
                        sk.pop(cursor)

                    else:
                        cursor += 1

                new_skeletons.append(deepcopy(skeleton))

        skeletons = new_skeletons
        print(f"{j}: {nice_decomp_node}")
        print(len(skeletons))
        for skeleton in skeletons:
            print(skeleton)
        print("END\n")

    best_skel = skeletons[0]
    for skeleton in skeletons[1:]:
        if skeleton.width < best_skel.width:
            best_skel = skeleton

    for node in best_skel.skeleton:
        print(node)



if __name__ == "__main__":
    main()