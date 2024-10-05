import pydot, sys
from pydot.core import Dot, Subgraph, Node, Edge
from enum import Enum, auto

class NodeType(Enum):
    BASIC = auto()
    MERGE = auto()
    IF = auto()
    WHILE = auto()
    DO_WHILE_START = auto()
    DO_WHILE_END = auto()
    SWITCH = auto()
    RETURN = auto()
    ENTRY = auto()
    EXIT = auto()

class EdgeType(Enum):
    SINGLE = auto()
    IF = auto()
    ELSE = auto()
    LOOP = auto()
    END = auto()
    SWITCH = auto()



class Snode:
    if_count = 0
    merged: list['Snode'] = []

    def __init__(self, name: str, inloops: list[str], label: str):
        self.name = name
        self.incoming_edges: list[Sedge] = []
        self.outgoing_edges: list[Sedge] = []
        self.inloops = inloops[:]
        self.label = label
        self.type: NodeType = None

    def determineType(self):
        if self.type != None: # type already set
            return

        incoming_edge_types: list[EdgeType] = [edge.type for edge in self.incoming_edges]
        outgoing_edge_types: list[EdgeType] = [edge.type for edge in self.outgoing_edges]



        if incoming_edge_types.count(EdgeType.IF) > 1:
            self.mergeNodes([node for node in self.incoming_edges if node.type == EdgeType.IF], EdgeType.IF)
            incoming_edge_types: list[EdgeType] = [edge.type for edge in self.incoming_edges]

        if incoming_edge_types.count(EdgeType.ELSE) > 1:
            self.mergeNodes([node for node in self.incoming_edges if node.type == EdgeType.ELSE], EdgeType.ELSE)
            incoming_edge_types: list[EdgeType] = [edge.type for edge in self.incoming_edges]


        if EdgeType.SWITCH in outgoing_edge_types:
            self.type = NodeType.SWITCH

        elif EdgeType.LOOP in incoming_edge_types:
            if (len(outgoing_edge_types) == 2 
                and EdgeType.IF in outgoing_edge_types
                and EdgeType.ELSE in outgoing_edge_types):

                self.type = NodeType.WHILE

            else:
                self.type = NodeType.DO_WHILE_START

        elif EdgeType.ELSE in outgoing_edge_types:
            if EdgeType.IF in outgoing_edge_types:
                self.type = NodeType.IF

            elif EdgeType.LOOP in outgoing_edge_types:
                self.type = NodeType.DO_WHILE_END

        elif EdgeType.IF in outgoing_edge_types:
            if EdgeType.LOOP in outgoing_edge_types:
                self.type = NodeType.IF

        elif EdgeType.END in outgoing_edge_types:
            self.type = NodeType.RETURN

        elif len(outgoing_edge_types) == 1:
            if len(incoming_edge_types) == 1:
                self.type = NodeType.BASIC

            else:
                self.type = NodeType.MERGE

        assert self.type != None # Every node should get a type
        

    def mergeNodes(self, nodes: list['Snode'], inc_edge_type: EdgeType):
        assert inc_edge_type in (EdgeType.IF, EdgeType.ELSE)

        # 'self' = merge node

        first = Snode.getFirstInGroup(nodes)
        last = Snode.getLastInGroup(nodes)

        to_remove = [edge for edge in self.incoming_edges
                    if (edge.source != first and edge.type == inc_edge_type)]

        # remove edges going into merge node from nodes to be pruned (1)
        for edge in to_remove:
            for node in nodes:
                try:
                    node.outgoing_edges.remove(edge)
                except ValueError:
                    assert edge.source != node
            
            self.incoming_edges.remove(edge)

        for node in nodes:
            if node != first:
                for edge in node.incoming_edges: # remove edges into nodes to be pruned
                    edge.source.outgoing_edges.remove(edge)

                if node != last:
                    for edge in node.outgoing_edges: # remove edges from nodes to be pruned (except 'last' node)
                        edge.destination.incoming_edges.remove(edge)
                        print("REMOVED EDGE!")

        assert len(last.outgoing_edges) == 1 
        # 'last' should only have one outgoing edge since its edge into merge node was removed in (1)

        last.outgoing_edges[0].source = first
        first.outgoing_edges.append(last.outgoing_edges[0])
        # modify this edge's source from 'last' to 'first' and append it to 'first's outgoing edges
        # this finalises the merge process since now 'first' replaces all the nodes in the CFG structure whilst
        # maintaining connectivty

    @staticmethod
    def getFirstInGroup(nodes: list['Snode']) -> 'Snode':
        for node in nodes:
            for edge in node.incoming_edges:
                if edge.type != EdgeType.LOOP and edge.source in nodes:
                    break

            else:
                return node
            
    @staticmethod
    def getLastInGroup(nodes: list['Snode']) -> 'Snode':
        for node in nodes:
            for edge in node.outgoing_edges:
                if edge.type != EdgeType.LOOP and edge.destination in nodes:
                    break

            else:
                return node
            
    def getIfElseEdges(self) -> tuple['Sedge', 'Sedge']:
        assert self.type == NodeType.IF
        assert len(self.outgoing_edges) == 2

        if self.outgoing_edges[0].type == EdgeType.LOOP:
            return self.outgoing_edges[0], self.outgoing_edges[1]
        
        elif self.outgoing_edges[1].type == EdgeType.LOOP:
            return self.outgoing_edges[1], self.outgoing_edges[0]
        
        elif self.outgoing_edges[0].type == EdgeType.IF:
            return self.outgoing_edges[0], self.outgoing_edges[1]
        
        elif self.outgoing_edges[1].type == EdgeType.IF:
            return self.outgoing_edges[1], self.outgoing_edges[0]
        
        raise KeyError()
            
    def getWhileDoneEdges(self) -> tuple['Sedge', 'Sedge']:
        assert self.type == NodeType.WHILE
        assert len(self.outgoing_edges) == 2

        if len(self.outgoing_edges[0].destination.inloops) == len(self.inloops):
            return self.outgoing_edges[0], self.outgoing_edges[1]
        
        return self.outgoing_edges[1], self.outgoing_edges[0]
    
    def find_merge(self, if_edge: 'Sedge') -> bool:
        def isBreak(edge: Sedge) -> bool:
            return len(edge.source.inloops) != len (edge.destination.inloops)
        
        def trace(node: Snode, if_depth: int) -> Snode | None:
            if len(node.incoming_edges) > 1:
                if if_depth == 0:
                    return node
                if_depth -= 1
            
            for edge in node.outgoing_edges:
                if edge.type == EdgeType.LOOP or isBreak(edge):
                    continue

                if edge.type in (EdgeType.IF, EdgeType.ELSE):
                    if (ret := trace(edge.destination, if_depth + 1)) != None:
                        return ret
                else:
                    if (ret := trace(edge.destination, if_depth)) != None:
                        return ret
                    
            return None
        
        self.found = trace(if_edge.destination, 0)
        if self.found != None:
            assert len(self.found.incoming_edges) > 1

            if self.found in Snode.merged:
                return False
            
            Snode.merged.append(self.found)
            return True
        
        return False
            
    def __str__(self):
        match self.type:
            case NodeType.BASIC:
                if self.outgoing_edges[0].destination.type == NodeType.MERGE:
                    return f'o{self.name.split("_")[-1]}'
                if self.outgoing_edges[0].destination.type == NodeType.RETURN:
                    if self.outgoing_edges[0].destination in Snode.merged:
                        return f'o{self.name.split("_")[-1]}'
                if self.outgoing_edges[0].type == EdgeType.SINGLE:
                    return f"o{self.name.split("_")[-1]} {self.outgoing_edges[0].destination}"
                return f'o{self.name.split("_")[-1]}'
            
            case NodeType.MERGE:
                if self.outgoing_edges[0].destination.type == NodeType.MERGE:
                    return f'o{self.name.split("_")[-1]}'
                if self.outgoing_edges[0].destination.type == NodeType.RETURN:
                    if self.outgoing_edges[0].destination in Snode.merged:
                        return f'o{self.name.split("_")[-1]}'
                if self.outgoing_edges[0].type == EdgeType.SINGLE:
                    return f"o{self.name.split("_")[-1]} {self.outgoing_edges[0].destination}"
                return f'o{self.name.split("_")[-1]}'
            
            case NodeType.RETURN:
                return f"o{self.name.split("_")[-1]} {self.outgoing_edges[0].destination}"
            
            case NodeType.ENTRY:
                return f"p {self.outgoing_edges[0].destination}"

            case NodeType.EXIT:
                return "m"
            
            case NodeType.WHILE:
                loop_edge, done_edge = self.getWhileDoneEdges()

                return f"w{self.inloops[-1].split(" ")[-1]} {loop_edge.destination} d{self.inloops[-1].split(" ")[-1]} {done_edge.destination}"
            
            case NodeType.IF:
                count = Snode.if_count
                Snode.if_count += 1

                if_edge, else_edge = self.getIfElseEdges()

                # if one of the edges is a loop edge, it will be the if_edge, due to
                # getIfElseEdges implementation
                if if_edge.type == EdgeType.LOOP:
                    if_block = f"c{self.inloops[-1].split(" ")[-1]}"
                    else_block = ""
                    merge_block = f"{else_edge.destination}"

                elif self.find_merge(if_edge):
                    if_block = str(if_edge.destination)
                    else_block = f" e{count} {else_edge.destination}"
                    merge_block = str(self.found)

                else:
                    if_block = str(if_edge.destination)
                    else_block = f" e{count} {else_edge.destination}"
                    merge_block = ""

                if else_edge.destination.type == NodeType.MERGE:
                    else_block = ""
                    merge_block = f"{else_edge.destination}"

                # elif else_edge.type == EdgeType.LOOP:
                #     else_block = " else {\n" + f"continue_{self.inloops[-1].split(" ")[-1]}" + "\n}"

                #print(f"DEBUG: {self.name}: '{merge_block}'")

                return f"i{count} {if_block}{else_block} f{count}{' ' if merge_block != '' else ''}{merge_block}"

class Sedge:
    def __init__(self, source: Snode, destination: Snode, dot_edge: Edge):
        self.source = source
        self.destination = destination

        match dot_edge.get_attributes():
            case {'style': '"dotted,bold"', 'color': 'blue'}:
                self.type = EdgeType.LOOP

            case {'style': '"solid,bold"', 'color': 'black', 'weight': '10'}:
                if self.destination.name[-13:] == "basic_block_1":
                    self.type = EdgeType.END
                else:
                    self.type = EdgeType.SWITCH

            case {'style': '"solid,bold"', 'color': 'forestgreen', 'weight': '10'}:
                self.type = EdgeType.IF

            case {'style': '"solid,bold"', 'color': 'darkorange', 'weight': '10'}:
                self.type = EdgeType.ELSE

            case {'style': '"solid,bold"', 'color': 'black', 'weight': '100'}:
                self.type = EdgeType.SINGLE

            case _:
                raise Exception(f"No edge type found for edge from {source} to {destination}")
            
input_graph: Dot = pydot.graph_from_dot_file(sys.argv[1])[0]
main_sg: Subgraph = input_graph.get_subgraph('"cluster_main"')[0]
input_graph_edges: list[Edge] = main_sg.get_edge_list()

# Construct dictionary of nodes
nodes: dict[str, Snode] = {}

# Initialise list to store which loops each node is within
sgs_to_iterate: list[Subgraph] = [main_sg]
inloops: list[str] = []

# Add nodes to the dictionary 
while sgs_to_iterate:
    sg_to_iterate = sgs_to_iterate.pop(0)

    """
    If the subgraph is a string, that means
    it is a marker to remove that subgraph name
    from inloops, since the subsequent subgraphs
    are no longer within that subgraph
    """
    if isinstance(sg_to_iterate, str):
        inloops.remove(sg_to_iterate)
        continue

    sg_label = sg_to_iterate.get_attributes()["label"].strip('"')
    inloops.append(sg_label)

    # for node within the current subgraph
    for node in sg_to_iterate.get_nodes():
        # create a node object and add it to the node dictionary
        nodes[node.get_name()] = Snode(
                                    node.get_name(), 
                                    inloops, 
                                    node.get_attributes()["label"].strip('"')
                                )

    # prepend subgraphs of the current subgraph to the list of subgraphs still left to iterate
    # 'sg_label' is also prepended as a marker to tell the loop that we have exited the subgraph
    sgs_to_iterate = [*sg_to_iterate.get_subgraphs(), sg_label, *sgs_to_iterate]

# Add edges to nodes
for edge in input_graph_edges:
    if edge.get_attributes()['style'] == '"invis"':
        continue

    destination = edge.get_destination()[:-2]
    source = edge.get_source()[:-2]

    new_edge = Sedge(nodes[source], nodes[destination], edge)

    nodes[source].outgoing_edges.append(new_edge)
    nodes[destination].incoming_edges.append(new_edge)

# Find start and end nodes
for node in nodes.values():
    if node.label == 'ENTRY':
        entry_node = node
        
    elif node.label == 'EXIT':
       exit_node = node

entry_node.type = NodeType.ENTRY
exit_node.type = NodeType.EXIT

for node in nodes.values():
    node.determineType()

print(entry_node)