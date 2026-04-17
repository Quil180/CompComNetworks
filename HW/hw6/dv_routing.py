#!/usr/bin/env python3
"""
Distance Vector (DV) Routing Algorithm Implementation
HW6 - Computer Communications & Networks
Author: Yousef Alaa Awad

Implements the Bellman-Ford based DV routing algorithm for:
  Task 1-1: A 2x2 (4-node) network
  Task 1-2: A 4x4 (16-node) network with random edge weights
"""

import random
import math
import copy

INF = math.inf


def build_2x2_network():
    """
    Build the 2x2 grid network from Figure 1.
    Nodes: a, b, c, d arranged as:
        a --- b
        |     |
        c --- d
    Edge weights chosen as representative values.
    """
    nodes = ['a', 'b', 'c', 'd']
    # Adjacency: (node1, node2, cost)
    edges = [
        ('a', 'b', 1),
        ('a', 'c', 2),
        ('b', 'd', 4),
        ('c', 'd', 6),
    ]
    return nodes, edges


def build_4x4_network(seed=42):
    """
    Build a 4x4 grid network (16 nodes) with random edge weights in [1, 10].
    Nodes labeled 0-15, arranged in a grid:
        0  -  1  -  2  -  3
        |     |     |     |
        4  -  5  -  6  -  7
        |     |     |     |
        8  -  9  - 10 - 11
        |     |     |     |
       12 - 13 - 14 - 15
    """
    random.seed(seed)
    N = 4
    nodes = list(range(N * N))
    edges = []
    for r in range(N):
        for c in range(N):
            node = r * N + c
            # Right neighbor
            if c + 1 < N:
                right = r * N + (c + 1)
                cost = random.randint(1, 10)
                edges.append((node, right, cost))
            # Down neighbor
            if r + 1 < N:
                down = (r + 1) * N + c
                cost = random.randint(1, 10)
                edges.append((node, down, cost))
    return nodes, edges


def initialize_dv_tables(nodes, edges):
    """
    Initialize distance vector tables for all nodes.
    Each node's DV table is a dict mapping destination -> estimated cost.
    Initially, a node knows: cost to itself = 0, cost to neighbors = link cost,
    cost to all other nodes = infinity.
    Also returns the adjacency list (neighbors of each node).
    """
    # Build adjacency list
    neighbors = {n: {} for n in nodes}
    for u, v, cost in edges:
        neighbors[u][v] = cost
        neighbors[v][u] = cost

    # Initialize DV tables: dv[node][dest] = estimated distance from node to dest
    dv = {}
    for n in nodes:
        dv[n] = {}
        for dest in nodes:
            if dest == n:
                dv[n][dest] = 0
            elif dest in neighbors[n]:
                dv[n][dest] = neighbors[n][dest]
            else:
                dv[n][dest] = INF
    return dv, neighbors


def print_dv_tables(nodes, dv, iteration, label=""):
    """
    Print all DV tables for a given iteration in a readable format.
    Each node's table shows estimated distances to all destinations.
    """
    header = f"{'':>6}" + "".join(f"{str(d):>6}" for d in nodes)

    if label:
        print(f"\n{'='*60}")
        print(f"  {label} - Iteration {iteration}")
        print(f"{'='*60}")
    else:
        print(f"\n--- Iteration {iteration} ---")

    for n in nodes:
        print(f"\n  DV table at node {n}:")
        print(f"  {header}")
        # In a full DV table, node n stores what it believes the distance
        # from itself to every destination is.
        row = f"  {str(n):>6}"
        for dest in nodes:
            val = dv[n][dest]
            if val == INF:
                row += f"{'inf':>6}"
            else:
                row += f"{val:>6}"
        print(row)


def run_dv(nodes, edges, label=""):
    """
    Run the Distance Vector routing algorithm until convergence.
    In each iteration, every node sends its distance vector to its neighbors.
    Each neighbor updates its own DV using the Bellman-Ford equation:
        D_x(y) = min over all neighbors v of { c(x,v) + D_v(y) }
    The algorithm terminates when no DV table changes in an iteration.
    """
    dv, neighbors = initialize_dv_tables(nodes, edges)

    # Print initial state (iteration 0)
    print_dv_tables(nodes, dv, 0, label)

    iteration = 0
    while True:
        iteration += 1
        changed = False
        # Create a snapshot of current DV tables so all nodes use
        # the same "round" of information (synchronous update)
        old_dv = copy.deepcopy(dv)

        for n in nodes:
            for dest in nodes:
                if dest == n:
                    continue
                # Bellman-Ford: check all neighbors for a shorter path
                best = old_dv[n][dest]
                for nbr, link_cost in neighbors[n].items():
                    candidate = link_cost + old_dv[nbr][dest]
                    if candidate < best:
                        best = candidate
                if best != dv[n][dest]:
                    dv[n][dest] = best
                    changed = True

        print_dv_tables(nodes, dv, iteration, label)

        if not changed:
            print(f"\n  >> Converged after {iteration} iteration(s).")
            break

    return iteration


def main():
    # ---- Task 1-1: 2x2 Network ----
    print("=" * 70)
    print("  TASK 1-1: DV Routing for 2x2 (4-node) Network")
    print("=" * 70)
    nodes_2x2, edges_2x2 = build_2x2_network()
    print("\n  Network topology:")
    for u, v, c in edges_2x2:
        print(f"    {u} -- {v} : cost {c}")
    iters_2x2 = run_dv(nodes_2x2, edges_2x2, label="Task 1-1")

    # ---- Task 1-2: 4x4 Network ----
    print("\n\n" + "=" * 70)
    print("  TASK 1-2: DV Routing for 4x4 (16-node) Network")
    print("=" * 70)
    nodes_4x4, edges_4x4 = build_4x4_network(seed=42)
    print("\n  Network topology (random weights, seed=42):")
    for u, v, c in edges_4x4:
        print(f"    {u:>2} -- {v:>2} : cost {c}")
    iters_4x4 = run_dv(nodes_4x4, edges_4x4, label="Task 1-2")

    # ---- Summary ----
    print("\n\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Task 1-1 (2x2): Converged in {iters_2x2} iteration(s)")
    print(f"  Task 1-2 (4x4): Converged in {iters_4x4} iteration(s)")


if __name__ == "__main__":
    main()
