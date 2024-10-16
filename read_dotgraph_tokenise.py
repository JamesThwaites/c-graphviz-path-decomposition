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

        incoming_edge_types: list[EdgeType] = [edge.type for edge in self.incoming_edges]
        outgoing_edge_types: list[EdgeType] = [edge.type for edge in self.outgoing_edges]


        try:
            if incoming_edge_types.count(EdgeType.IF) > 1:
                self.mergeNodes([edge.source for edge in self.incoming_edges if edge.type == EdgeType.IF], EdgeType.IF)
                incoming_edge_types: list[EdgeType] = [edge.type for edge in self.incoming_edges]

            if incoming_edge_types.count(EdgeType.ELSE) > 1:
                self.mergeNodes([edge.source for edge in self.incoming_edges if edge.type == EdgeType.ELSE], EdgeType.ELSE)
                incoming_edge_types: list[EdgeType] = [edge.type for edge in self.incoming_edges]
        
        except ValueError as e:
            #print(self.name + ":", e, file=sys.stderr)
            return

        if EdgeType.SWITCH in outgoing_edge_types:
            self.type = NodeType.SWITCH

        elif EdgeType.LOOP in incoming_edge_types:
            if (len(outgoing_edge_types) == 2 
                and EdgeType.IF in outgoing_edge_types
                #and EdgeType.ELSE in outgoing_edge_types
            ):

                self.type = NodeType.WHILE
                _, done_edge = self.getWhileDoneEdges()
                Snode.dones[done_edge.destination] = self.inloops[-1]

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
            # if len(incoming_edge_types) == 1:
            self.type = NodeType.BASIC

            # else:
            #     self.type = NodeType.MERGE

        assert self.type != None # Every node should get a type
        

    def mergeNodes(self, nodes: list['Snode'], inc_edge_type: EdgeType):
        assert inc_edge_type in (EdgeType.IF, EdgeType.ELSE)

        # print("merging onto node:", self.name)
        # print("nodes to merge:", [node.name for node in nodes])

        # 'self' = merge node
        first, connected1 = Snode.getFirstInGroup(nodes)
        last, connected2 = Snode.getLastInGroup(nodes)

        if not (connected1 or connected2):
            raise ValueError("Nodes provided are not connected, will re-attempt merge later")

        to_remove = [edge for edge in self.incoming_edges
                    if (edge.source != first 
                    and edge.type == inc_edge_type)]

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
                        # print("REMOVED EDGE!", edge.source.name, edge.destination.name)

        # print(last.name)
        assert len(last.outgoing_edges) == 1 
        # 'last' should only have one outgoing edge since its edge into merge node was removed in (1)

        last.outgoing_edges[0].source = first
        first.outgoing_edges.append(last.outgoing_edges[0])
        # modify this edge's source from 'last' to 'first' and append it to 'first's outgoing edges
        # this finalises the merge process since now 'first' replaces all the nodes in the CFG structure whilst
        # maintaining connectivty
        # print(first.name, [edge.destination.name for edge in first.outgoing_edges])

    @staticmethod
    def getFirstInGroup(nodes: list['Snode']) -> tuple['Snode', bool]:
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
                if if_depth == 0:
                    return edge
                if_depth -= 1
            
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
                    #print(self.name, self.found.name)
                    if self.found not in Snode.merged:
                        merge_block = str(self.found)
                        Snode.merged.add(self.found)

                    else:
                        merge_block = ""

                    if_block = str(if_edge.destination)

                    if else_edge.destination != self.found:
                        else_block = f" e{count} {else_edge.destination}"

                    


                else:
                    # account for continue statements
                    if self.found.type == NodeType.WHILE:
                        if_block = f"{if_edge.destination} c{self.found.inloops[-1].split()[-1]}"

                    # account for break and return statements
                    else:
                        if_block = str(if_edge.destination)
                    
                    if else_edge.type != EdgeType.LOOP:
                        merge_block = f"{else_edge.destination}"

                        # if there's a break in the else_block
                        # if len(else_edge.destination.inloops) != len(self.inloops):
                        #     merge_block += f" b{self.inloops[-1].split()[-1]}"
                        
                        # if there's a break in the else_block
                        # if len(else_edge.destination.inloops) != len(self.inloops):
                        #     else_block += f" b{self.inloops[-1].split()[-1]}"

                    # if else_edge.destination.type == NodeType.MERGE: # questionable?
                    #     else_block = ""
                    #     merge_block = f"{else_edge.destination}"

                # elif else_edge.type == EdgeType.LOOP:
                #     else_block = " else {\n" + f"continue_{self.inloops[-1].split()[-1]}" + "\n}"
                # print(self.name, self.found.name, if_block)
                #print(self.label)
                #print(f"DEBUG: {self.name}: '{merge_block}'")
                return f"i{count} {if_block}{else_block} f{count}{' ' if merge_block != '' else ''}{merge_block}"
                #return f"o{self.name.split("_")[-1]} i{count} {if_block}{else_block} f{count}{' ' if merge_block != '' else ''}{merge_block}"

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
        if new_edge.type != EdgeType.LOOP:
            nodes[destination].non_loop_in_edge_count += 1

    # Find start and end nodes
    for node in nodes.values():
        if node.label == 'ENTRY':
            entry_node = node
            
        elif node.label == 'EXIT':
            exit_node = node

    entry_node.type = NodeType.ENTRY
    exit_node.type = NodeType.EXIT

    while True:
        for node in nodes.values():
            node.determineType()

        for node in nodes.values():
            if node.type == None:
                break
        
        else:
            break

    # for node in nodes.values():
    #     print(node.name, node.type, [(e.destination.name, e.type) for e in node.outgoing_edges])
    
    if graph_file_name == '':
        print(f"{entry_node} {exit_node}")
        # for b in Snode.breaks:
        #     print(b.source.name, b.destination.name)

    else:
        return f"{entry_node} {exit_node}"

if __name__ == "__main__":
    main()