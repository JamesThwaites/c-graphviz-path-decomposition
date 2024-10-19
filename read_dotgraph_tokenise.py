import pydot
import sys
import re
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
    DISCONNECTED = auto()

class EdgeType(Enum):
    SINGLE = auto()
    IF = auto()
    ELSE = auto()
    LOOP = auto()
    END = auto()
    SWITCH = auto()



class Snode:
    if_count = 0
    ret_count = -1
    merged: set['Snode'] = set()
    dones: dict['Snode', str] = {}
    breaks: set['Sedge'] = set()

    def __init__(self, name: str, inloops: list[str], label: str):
        self.name = name
        self.non_loop_in_edge_count: int = 0
        self.incoming_edges: list[Sedge] = []
        self.outgoing_edges: list[Sedge] = []
        self.inloops = inloops[:]
        self.label = label
        self.type: NodeType = None

    def determineType(self):
        if self.type != None: # type already set
            return
        
        incoming_edge_types = [edge.type for edge in self.incoming_edges]
        outgoing_edge_types = [edge.type for edge in self.outgoing_edges]

        if EdgeType.LOOP in incoming_edge_types:
            if (len(outgoing_edge_types) == 2 
                and EdgeType.IF in outgoing_edge_types
                #and EdgeType.ELSE in outgoing_edge_types
            ):

                self.type = NodeType.WHILE
                _, done_edge = self.getWhileDoneEdges()
                Snode.dones[done_edge.destination] = self.inloops[-1]

            else:
                self.type = NodeType.DO_WHILE_START
                print("DO_WHILE_START:", self.name)
                raise ValueError("Do-while blocks are unsupported!")

        elif EdgeType.ELSE in outgoing_edge_types:
            if EdgeType.IF in outgoing_edge_types:
                self.type = NodeType.IF

            elif EdgeType.LOOP in outgoing_edge_types:
                self.type = NodeType.DO_WHILE_END
                print("DO_WHILE_END:", self.name)
                raise ValueError("Do-while blocks are unsupported!")

        elif EdgeType.IF in outgoing_edge_types:
            if EdgeType.LOOP in outgoing_edge_types:
                self.type = NodeType.IF

        elif EdgeType.END in outgoing_edge_types:
            self.type = NodeType.RETURN

        elif len(outgoing_edge_types) == 1:
            # if len(incoming_edge_types) == 1:
            self.type = NodeType.BASIC

            # else:
            #     self.type = NodeType.MERGE

        assert self.type != None # Every node should get a type
        

    def mergeNodes(self, nodes: list['Snode'], inc_edge_type: EdgeType):
        """Merges the CFG nodes making up a multi-conditional statement
        with one end at ```self```.
        
        A multi-conditional is an ```if``` or ```while``` statement
        with multiple conditions (e.g. ```if x1 and x2```)
        """
        assert inc_edge_type in (EdgeType.IF, EdgeType.ELSE)

        # self = 'merge node'

        # first = node evaluating the first conditional
        first, connected1 = Snode.getFirstInGroup(nodes)
        # last = node evaluating the last conditional
        last, connected2 = Snode.getLastInGroup(nodes)

        if not (connected1 or connected2):
            raise ValueError("Nodes provided are not connected, "
                             "will re-attempt merge later")

    #   (1) Remove edges going into merge node from nodes to be pruned
        to_remove = [edge for edge in self.incoming_edges
                    if (edge.source != first 
                    and edge.type == inc_edge_type)]

        for edge in to_remove:
            for node in nodes:
                try:
                    node.outgoing_edges.remove(edge)
                except ValueError:
                    assert edge.source != node
            
            self.incoming_edges.remove(edge)
            if edge.type != EdgeType.LOOP:
                # Maintain correct count
                self.non_loop_in_edge_count -= 1

    #   Remove other edges from nodes to be pruned
        for node in nodes:
            if node != first:
                node.type = NodeType.DISCONNECTED

                # Remove outgoing edges into nodes to be pruned
                for edge in node.incoming_edges: 
                    edge.source.outgoing_edges.remove(edge)
                    # Edges that are removed are outgoing into nodes 
                    # that will be removed from the CFG.

                    # The other direction of the edges may not be
                    # removed in the next step but it doesn't matter
                    # as the other direction is incoming edges on
                    # nodes that will be deleted anyway.

                if node != last:
                    # Remove incoming edges from nodes to be pruned
                    # except 'last'
                    for edge in node.outgoing_edges:
                        edge.destination.incoming_edges.remove(edge)

                        if edge.type != EdgeType.LOOP:
                            edge.destination.non_loop_in_edge_count -= 1
                        # print("REMOVED EDGE!", edge.source.name, edge.destination.name)

        # print(last.name)
        assert len(last.outgoing_edges) == 1 
        # 'last' should only have one outgoing edge since its edge 
        # into the merge node was removed in (1)

        last.outgoing_edges[0].source = first
        first.outgoing_edges.append(last.outgoing_edges[0])
        # modify this edge's source from 'last' to 'first' and append it to 'first's outgoing edges
        # this finalises the merge process since now 'first' replaces all the nodes in the CFG structure whilst
        # maintaining connectivty

        # print(first.name, [edge.destination.name for edge in first.outgoing_edges])
        # if first.type == NodeType.WHILE:
        #     print([e.destination.name for e in first.getWhileDoneEdges()])

    @staticmethod
    def getFirstInGroup(nodes: list['Snode']) -> tuple['Snode', bool]:
        """Finds and returns the 'first' node in ```nodes```.
        
        The 'first' node is the node with no incoming edge from any
        other node in ```nodes```.
        
        The second return value is a flag indicating whether the 
        graph of ```nodes``` is connected (i.e. whether a path exists
        between every pair of nodes)
        """
        group_connected = False
        to_ret = None
        for node in nodes:
            for edge in node.incoming_edges:
                if edge.type != EdgeType.LOOP and edge.source in nodes:
                    group_connected = True
                    break

            else:
                to_ret = node

        return to_ret, group_connected
            
    @staticmethod
    def getLastInGroup(nodes: list['Snode']) -> tuple['Snode', bool]:
        """Finds and returns the 'last' node in ```nodes```.
        
        The 'last' node is the node with no outgoing edge to any
        other node in ```nodes```.
        
        The second return value is a flag indicating whether the 
        graph of ```nodes``` is connected (i.e. whether a path exists
        between every pair of nodes)
        """
        group_connected = False
        to_ret = None
        for node in nodes:
            for edge in node.outgoing_edges:
                if edge.type != EdgeType.LOOP and edge.destination in nodes:
                    group_connected = True
                    break

            else:
                to_ret = node

        return to_ret, group_connected
            
    def getIfElseEdges(self) -> tuple['Sedge', 'Sedge']:
        assert self.type == NodeType.IF
        assert len(self.outgoing_edges) == 2

        if self.outgoing_edges[0].type == EdgeType.LOOP:
            return self.outgoing_edges[1], self.outgoing_edges[0]
        
        elif self.outgoing_edges[1].type == EdgeType.LOOP:
            return self.outgoing_edges[0], self.outgoing_edges[1]
        
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
    
    def findMerge(self, if_edge: 'Sedge') -> bool:
        """
        Assigns self.found equal to the last statement after the
        block of 'if_edge', whether that is a 'true merge' (i.e.
        where the if and else blocks rejoin) if one exists, or 
        a node that breaks out of the block (i.e. a 'break', 
        'return' or 'continue')
        
        Returns True if there is a 'true merge' and False otherwise
        """

        def isReturn(edge: Sedge) -> bool:
            return edge.destination.type == NodeType.RETURN

        def isBreak(edge: Sedge) -> bool:
            #print(edge.source.name, edge.source.inloops, edge.destination.name, edge.destination.inloops)
            return edge.destination in Snode.dones and Snode.dones[edge.destination] in self.inloops
        
        def isContinue(edge: Sedge) -> bool:
            # print(edge.source.name, edge.source.inloops, edge.destination.name, edge.destination.inloops)
            # print(edge.type == EdgeType.LOOP and edge.destination.inloops[-1] == self.inloops[-1])
            return edge.type == EdgeType.LOOP and edge.destination.inloops[-1] == self.inloops[-1]
        
        def trace(edge: Sedge, if_depth: int) -> Sedge | None:
            # if edge leads to a 'continue', 'return' or 'break'
            if isContinue(edge) or isReturn(edge) or isBreak(edge):
                return edge
            
            # Account for loop edges that aren't continues
            # They could appear in nested loops
            if edge.type == EdgeType.LOOP:
                return None
            
            if edge.destination.non_loop_in_edge_count > 1 and edge.destination not in Snode.dones:
                if_depth -= (edge.destination.non_loop_in_edge_count - 1)
                if if_depth < 0:
                    return edge
                
            
            for out_edge in edge.destination.outgoing_edges:
                if out_edge.type in (EdgeType.IF, EdgeType.ELSE) and edge.destination.type == NodeType.IF:
                    if (ret := trace(out_edge, if_depth + 1)) != None:
                        return ret
                else:
                    if (ret := trace(out_edge, if_depth)) != None:
                        return ret
                    
            return None
        
        self.found = trace(if_edge, 0)
        #print(self.name, if_edge.destination.name)
        assert self.found != None # should always be one in expected cases

        # if there is no merge due to a continue
        if isContinue(self.found):
            self.found = self.found.destination
            # i.e. self.found = the WHILE node after the continue edge
            return False
        
        # if there is no merge due to a return or break
        elif isReturn(self.found):
            self.found = self.found.source
            # i.e. self.found = the node before the RETURN node
            # after the edge
            return False
        
        elif isBreak(self.found):
            for inc_edge in self.found.destination.incoming_edges:
                if inc_edge.source.inloops[-1] != Snode.dones[self.found.destination]:
                    Snode.breaks.add(inc_edge)

            self.found = self.found.source
            # i.e. self.found = the node before the DONE node
            # after the edge
            return False

        # if there is a true merge
        else: 
            self.found = self.found.destination
            # print(self.name, self.found.name)
            assert len(self.found.incoming_edges) > 1

            # print("Merge:", self.name, self.found.name)
            return True
                    
    def __str__(self):
        match self.type:
            case NodeType.BASIC:
                if self.outgoing_edges[0] in Snode.breaks:
                    return f'o{self.name.split("_")[-1]} b{Snode.dones[self.outgoing_edges[0].destination].split()[-1]}'
                
                if (self.outgoing_edges[0].type == EdgeType.LOOP
                    or self.outgoing_edges[0].destination in Snode.merged
                ):
                    return f'o{self.name.split("_")[-1]}'
                
                if (self.outgoing_edges[0].destination.type == NodeType.RETURN):
                    Snode.ret_count += 1
                    return f'o{self.name.split("_")[-1]} r{Snode.ret_count}'
                
                return f"o{self.name.split("_")[-1]} {self.outgoing_edges[0].destination}"
            
            case NodeType.RETURN:
                # return f"o{self.name.split("_")[-1]} {self.outgoing_edges[0].destination}"
                return ""
            
            case NodeType.ENTRY:
                return f"p {self.outgoing_edges[0].destination}"

            case NodeType.EXIT:
                return "m"
            
            case NodeType.WHILE:
                loop_edge, done_edge = self.getWhileDoneEdges()
                ret = f"w{self.inloops[-1].split()[-1]} {loop_edge.destination} d{self.inloops[-1].split()[-1]}"
                if done_edge.type != EdgeType.LOOP:
                    ret += f" {done_edge.destination}"
                return ret
                #return f"w{self.inloops[-1].split()[-1]} {loop_edge.destination} d{self.inloops[-1].split()[-1]} {done_edge.destination}"
            
            case NodeType.IF:
                count = Snode.if_count
                Snode.if_count += 1

                if_edge, else_edge = self.getIfElseEdges()

                if_block = else_block = merge_block = ""
                
                # handle merge since this indicates no break/continue/return inside if block
                if self.findMerge(if_edge):
                    if_block = if_edge.destination

                    if else_edge.destination != self.found:
                        else_block = else_edge.destination

                    if self.found not in Snode.merged:
                        Snode.merged.add(self.found)                        
                        merge_block = self.found
                        
                    else:
                        merge_block = ""

                    

                    


                else:
                    # account for continue statements
                    if self.found.type == NodeType.WHILE:
                        if else_edge.type == EdgeType.LOOP:
                            if_block = if_edge.destination
                        
                        elif self.findMerge(else_edge) or self.found.type == NodeType.WHILE:
                            if_block = f"{if_edge.destination} c{self.found.inloops[-1].split()[-1]}"

                        else:
                            if_block = if_edge.destination
                            else_block = else_edge.destination

                    # account for break and return statements
                    # else block is definitely in the loop
                    else:
                        if_block = if_edge.destination
                    
                    if else_edge.type != EdgeType.LOOP and else_block == "" and else_edge.destination not in Snode.merged:
                        merge_block = else_edge.destination

                return f"i{count} {if_block}{f" e{count} " if else_block != '' else ''}{else_block} f{count}{' ' if merge_block != '' else ''}{merge_block}"

class Sedge:
    def __init__(self, source: Snode, destination: Snode, dot_edge: Edge):
        self.source = source
        self.destination = destination

        if dot_edge is None:
            return

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
                raise Exception(f"No edge type found for edge from {source.name} to {destination.name}")



def main(graph_file_name: str = ''):
    # reset Snode 
    # (for testing purposes/running on multiple graphs in a row)
    Snode.if_count = 0
    Snode.ret_count = -1
    Snode.merged = set()
    Snode.dones = {}
    Snode.breaks = set()

    if graph_file_name != '':
        input_graph: Dot = pydot.graph_from_dot_file(graph_file_name)[0]
    else:
        input_graph: Dot = pydot.graph_from_dot_file(sys.argv[1])[0]

    main_sg: Subgraph = input_graph.get_subgraph('"cluster_main"')[0]
    input_graph_edges: list[Edge] = main_sg.get_edge_list()

    # Construct dictionary of nodes {'node_name': object}
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

        # Prepend subgraphs of the current subgraph to the list of
        # subgraphs still left to iterate.
        # 'sg_label' is also prepended as a marker to tell the loop that we have exited the subgraph
        sgs_to_iterate = [*sg_to_iterate.get_subgraphs(), sg_label, *sgs_to_iterate]

    # Add edges to nodes
    for edge in input_graph_edges:
        if edge.get_attributes()['style'] == '"invis"':
            continue

        destination = edge.get_destination()[:-2]
        source = edge.get_source()[:-2]

        entry_edge = Sedge(nodes[source], nodes[destination], edge)

        nodes[source].outgoing_edges.append(entry_edge)
        nodes[destination].incoming_edges.append(entry_edge)
        if entry_edge.type != EdgeType.LOOP:
            nodes[destination].non_loop_in_edge_count += 1

    # Find start and end nodes
    for node in nodes.values():
        if node.label == 'ENTRY':
            entry_node = node
            
        elif node.label == 'EXIT':
            exit_node = node

    entry_node.type = NodeType.ENTRY
    exit_node.type = NodeType.EXIT

    # Merge multi-conditionals
    while True:
        for node in nodes.values():
            incoming_edge_types = [edge.type for edge in node.incoming_edges]

            try:
                if incoming_edge_types.count(EdgeType.IF) > 1:
                    node.mergeNodes([edge.source for edge in node.incoming_edges if edge.type == EdgeType.IF], EdgeType.IF)
                    incoming_edge_types: list[EdgeType] = [edge.type for edge in node.incoming_edges]
                    break

                if incoming_edge_types.count(EdgeType.ELSE) > 1:
                    node.mergeNodes([edge.source for edge in node.incoming_edges if edge.type == EdgeType.ELSE], EdgeType.ELSE)
                    incoming_edge_types: list[EdgeType] = [edge.type for edge in node.incoming_edges]
                    break
            
            # If merge isn't possible yet due to nodes being
            # disconnected, skip for now and come back later.
            except ValueError as e:
                #print(self.name + ":", e, file=sys.stderr)
                continue
        else:
            break

    # Reformat switch statments
    while True:
        # Look if there are any switches to format
        for node in nodes.values():
            outgoing_edge_types = [edge.type for edge in node.outgoing_edges]

            if EdgeType.SWITCH in outgoing_edge_types:
                case_nodes: list[Snode] = []

                # The node after the switch if there's no default case
                fallthrough_node = None
                
                for edge in node.outgoing_edges:
                    edge.destination.incoming_edges.remove(edge)

                    # The fallthrough node will have more than 1 in-edge
                    if len(edge.destination.incoming_edges) > 0:
                        if fallthrough_node != None:
                            raise ValueError("Switch cases without 'break' statements are unsupported!")
                        fallthrough_node = edge.destination                            

                    # Cases only have 1 in-edge, so 0 now
                    else:
                        case_nodes.append(edge.destination)
                    
                if fallthrough_node != None:
                    case_nodes.append(fallthrough_node)
                    # for edge in fallthrough_node.incoming_edges:
                    #     edge.source.outgoing_edges.remove(edge)

                new_nodes = [
                    Snode(
                        f"s_{s_node.name}",
                        s_node.inloops,
                        ""
                    )
                    for s_node in case_nodes[:-1]
                ]                    

                entry_edge = Sedge(node, new_nodes[0], None)
                entry_edge.type = EdgeType.SINGLE

                node.outgoing_edges = [entry_edge]
                new_nodes[0].incoming_edges = [entry_edge]
                
                for i, new_node in enumerate(new_nodes):
                    nodes[new_node.name] = new_node
                    new_node.non_loop_in_edge_count = 1
                    
                    if_edge = Sedge(
                                new_node,
                                case_nodes[i],
                                None
                            )
                    if_edge.type = EdgeType.IF

                    case_nodes[i].incoming_edges = [
                        if_edge
                    ]

                    if i + 1 < len(new_nodes):
                        else_edge = Sedge(
                                            new_node,
                                            new_nodes[i+1],
                                            None
                                        )
                        else_edge.type = EdgeType.ELSE

                        new_nodes[i+1].incoming_edges = [
                            else_edge
                        ]

                        new_node.outgoing_edges = [
                            if_edge, else_edge
                        ]

                    else:
                        else_edge = Sedge(
                                            new_node,
                                            case_nodes[-1],
                                            None
                                        )
                        else_edge.type = EdgeType.ELSE

                        case_nodes[-1].incoming_edges.append(
                            else_edge
                        )

                        new_node.outgoing_edges = [
                            if_edge, else_edge
                        ]

                    # print(new_node.name, [edge.destination.name for edge in new_node.outgoing_edges])
                break
        else:
            break

    # Compute node types
    for node in nodes.values():
        node.determineType()

    # for node in nodes.values():
    #     print(node.name, node.type, [(e.destination.name, e.type) for e in node.outgoing_edges])
    
    if graph_file_name == '':

        # for node in nodes.values():
        #     print(node.name, node.type, [edge.source.name for edge in node.incoming_edges])

        # for br in Snode.breaks:
        #     print(br.source.name, br.destination.name)

        # for d in Snode.dones:
        #     print(d.name, Snode.dones[d])
        
        print(f"{entry_node} {exit_node}")

    else:
        return f"{entry_node} {exit_node}"

if __name__ == "__main__":
    main()