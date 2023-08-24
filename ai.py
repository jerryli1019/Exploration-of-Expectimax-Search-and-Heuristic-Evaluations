from __future__ import absolute_import, division, print_function
import copy, random
from game import Game

MOVES = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
MAX_PLAYER, CHANCE_PLAYER = 0, 1 

class Node: 
    def __init__(self, state, player_type):
        self.state = (state[0], state[1])
        self.children = []

        self.player_type = player_type

    def is_terminal(self):
        return len(self.children) == 0


class AI:
    def __init__(self, root_state, search_depth=3): 
        self.root = Node(root_state, MAX_PLAYER)
        self.search_depth = search_depth
        self.simulator = Game(*root_state)

    def build_tree(self, node = None, depth = 0):
        if depth == 0 or node is None:
            return 
        if node.player_type == MAX_PLAYER:
            curr_state = self.simulator.current_state()
            for direction in range(4):
                self.simulator.set_state(curr_state[0], curr_state[1])
                if self.simulator.move(direction):
                    new_node = Node(self.simulator.current_state(), CHANCE_PLAYER)
                    node.children += [(direction, new_node)]
                    self.build_tree(new_node, depth-1)
        if node.player_type == CHANCE_PLAYER:
            open_space = self.simulator.get_open_tiles()
            curr_state = self.simulator.current_state()
            if len(open_space) == 0:
                return 
            for coord in open_space:
                self.simulator.set_state(curr_state[0], curr_state[1])
                self.simulator.tile_matrix[coord[0]][coord[1]] = 2
                update_state = self.simulator.current_state()
                new_node = Node(update_state, MAX_PLAYER)
                node.children += [new_node]
                self.build_tree(new_node, depth-1)

    def expectimax(self, node = None):
        if node is None:
            return
        if node.is_terminal():
            return None, node.state[1]
        elif node.player_type == MAX_PLAYER:
            direction, value = None, -float('inf')
            for n in node.children:
                _, new_val = self.expectimax(n[1])
                if new_val > value:
                    direction, value = n[0], new_val
            return direction, value
        elif node.player_type == CHANCE_PLAYER:
            value = 0
            for n in node.children:
                value = value + self.expectimax(n)[1]/len(node.children)
            return None, value
        else:
            return


    def compute_decision(self):
        self.build_tree(self.root, self.search_depth)
        direction, _ = self.expectimax(self.root)
        return direction

    def expectimax_ec(self, node = None):
        weight = [[2048, 1024, 64, 32],
                  [512, 128, 16, 2],
                  [256, 8, 2, 1],
                  [4, 2, 1, 1]]
        if node is None:
            return
        if node.is_terminal():
            return None, node.state[1]
        elif node.player_type == MAX_PLAYER:
            direction, value = None, -float('inf')
            for n in node.children:
                curr_matrix = n[1].state[0]
                tiles = sum([1 for i in range(4) for j in range(4) if curr_matrix[i][j] == 0])
                sums = sum([curr_matrix[i][j]*weight[i][j] for i in range(len(weight)) for j in range(len(weight[0]))])
                new_val = self.expectimax_ec(n[1])[1] + sums*0.1 + tiles*525
                if new_val > value:
                    direction, value = n[0], new_val
            return direction, value
        elif node.player_type == CHANCE_PLAYER:
            value = 0
            for n in node.children:
                value = value + self.expectimax_ec(n)[1]/len(node.children)
            return None, value
        else:
            return
        
    def compute_decision_ec(self):
        self.build_tree(self.root, 3)
        direction, _ = self.expectimax_ec(self.root)
        return direction

