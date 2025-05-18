import argparse
import solver_advanced
import time
from utils import Instance


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Instances parameters
    parser.add_argument('--agent', type=str, default='naive')
    parser.add_argument('--infile', type=str, default='instance/trivial_1.txt')
    parser.add_argument('--viz-node-limit', type=int, default=4500)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    instance = Instance(args.infile)

    print("***********************************************************")
    print("[INFO] Start the solving: Market study")
    print("[INFO] input file: %s" % instance.filepath)
    print("[INFO] number of nodes: %s" % (instance.N))
    print("[INFO] number of edges: %s" % (instance.M))
    print("***********************************************************")

    start_time = time.time()

    # Méthode à implémenter
    if args.agent == "advanced":
        # Your nice agent
        solution = solver_advanced.solve(instance)
    else:
        raise Exception("This agent does not exist")


    solving_time = round((time.time() - start_time) / 60,2)

    # You can disable the display if you do not want to generate the visualization
    if args.viz_node_limit >= instance.N:
        instance.visualize_solution(solution)

    instance.save_solution(solution)
    cohesion, validity = instance.solution_value_and_validity(solution)
    unique_nodes = instance.unique_nodes_in_solution(solution)
    no_missing_added = instance.no_missing_or_added_nodes(solution)
    no_disconnected_groups = instance.no_disconnected_groups_in_solution(solution)

    print("***********************************************************")
    print("[INFO] Solution obtained")
    print("[INFO] Execution time : %s minutes" % solving_time)
    print(f"[INFO] Cohesion : {cohesion}")
    print(f"[INFO] Sanity check passed : {validity}\n\t Unique nodes in solution: {unique_nodes}\n\t No missing or added nodes : {no_missing_added}\n\t No disconnected groups : {no_disconnected_groups}")
    print("***********************************************************")
