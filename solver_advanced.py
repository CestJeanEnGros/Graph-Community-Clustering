from utils import Instance, Solution, Node
import copy
import os
import numpy as np
import time
from collections import deque, defaultdict, Counter
import itertools
import tqdm
import random as rd

def solve(instance: Instance) -> Solution:
    """Write your code here

    Args:
        instance (Instance): An Instance object containing all you need to solve the problem

    Returns:
        Solution: A solution object initialized with 
                  a list of iterators on grouped node ids (int)
    """
    # Divers paramètres et constantes
    start_time = time.time()
    savedSolution = []
    iterationWithoutGain = 0
    t = 170
    T = 1
    V = 30

    # Solution initiale
    groups_of_node_dict, value = initialSolution(instance, 10)
    print(f"Valeur de la solution initiale : {value}")
    savedSolution.append((copy.deepcopy(groups_of_node_dict), value))

    # Phase 1
    i = 0
    while i < 10:
        # On vérifie le temps restants
        if (time.time() - start_time) > t: break

        print(f"Phase 1, ittération {i}")
        
        # On part de la solution initiale
        groups_of_node_dict, value = copy.deepcopy(savedSolution[0][0]), copy.deepcopy(savedSolution[0][1])
        
        k = 5
        while k > 0:
            # On vérifie le temps restants
            if (time.time() - start_time) > t: break

            # print(f"k actuel = {k}")
            voisinages = mergeKComm(instance, groups_of_node_dict, value, k, V)
            voisinages.sort(key=lambda v: v[1], reverse=True) 
            # Verification deu voisinage
            if len(voisinages) != 0:
                # Choix du meilleur voisin
                if voisinages[0][1] > value:
                    groups_of_node_dict = voisinages[0][0]
                    value = voisinages[0][1]
                    # print(f'Record obtenue par la {voisinages[0][2]} de communautés')
                    realSol = buildSolution(groups_of_node_dict)
                    # print(value, value - instance.solution_value(realSol))
                    # print(f"Nombre de groupe : {len(realSol.groups_dict)}")
                else:
                    # Décrémentation de k pour un voisinages plus détaillé
                    # print(f"Echec phase de voisinages avec {k} fusions")
                    k -= 1
        i+=1
        savedSolution.append((copy.deepcopy(groups_of_node_dict), value))

    # On repart de la meilleurs des solutions de la phase 1    
    savedSolution.sort(key=lambda s: s[1], reverse=True)
    groups_of_node_dict, value = copy.deepcopy(savedSolution[0][0]), copy.deepcopy(savedSolution[0][1])
    print(f" Meilleur solution de la phase 1 : {value}")
    savedSolution.append((copy.deepcopy(groups_of_node_dict), value))

    #Phase 2
    
    while True:
        print("Phase 2")
        # On vérifie le temps restants
        if (time.time() - start_time) > t: break

        
        k = 5
        while k > 0:
            # On vérifie le temps restants
            if (time.time() - start_time) > t: break

            voisinages = moveKNodes(instance, groups_of_node_dict, value, k, V)
            voisinages.sort(key=lambda v: v[1], reverse=True) 
            # Verification deu voisinage
            if len(voisinages) != 0:
                # Choix du meilleur voisin
                if voisinages[0][1] > value:
                    realSol = buildSolution(voisinages[0][0])
                    if instance.no_disconnected_groups_in_solution(realSol):
                        groups_of_node_dict = voisinages[0][0]
                        value = voisinages[0][1]
                        savedSolution[-1] = (copy.deepcopy(groups_of_node_dict), copy.deepcopy(value))
                        # print(f'Record obtenue par le {voisinages[0][2]} de {k} noeuds')
                        
                        # print(value, value - instance.solution_value(realSol))
                        # print(f"Nombre de groupe : {len(realSol.groups_dict)}")
                else:
                    # Décrémentation de k pour un voisinages plus détaillé
                    # print(f"Echec phase de voisinages avec {k} mouvements")
                    k -= 1

        # Phase pour s'échapper d'un minima local
        print("Phase anti minima locaux")
        voisinages = voisinages[:10]
        voisinages = list(filter(lambda x: instance.no_disconnected_groups_in_solution(buildSolution(x[0])), voisinages))
        if len(voisinages) != 0:
            voisin = rd.choice(voisinages)
            groups_of_node_dict, value = voisin[0], voisin[1]
            savedSolution.append((copy.deepcopy(groups_of_node_dict), value))
            print(value)
        

    savedSolution.sort(key=lambda s: s[1], reverse=True)
    best_sol = buildSolution(savedSolution[0][0])
    print(f"Valeur finale : {savedSolution[0][1]}")
    print(len(groups_of_node_dict_to_groups_dict(savedSolution[0][0])))
    return best_sol





def initialSolution(instance: Instance, N: int):
    """
        Créer une solution initiale
        """
    # Initialisation
    deg_of_comm_dict = {node.get_idx(): node.degree() for node in instance.nodes}
    groups_of_node_dict = {node.get_idx(): node.get_idx() for node in instance.nodes}
    groups_dict = groups_of_node_dict_to_groups_dict(groups_of_node_dict)
    print(len(groups_dict))

    groups_of_node_dict, deg_of_comm_dict, v = nodesShift(instance, groups_of_node_dict, deg_of_comm_dict)
    groups_dict = groups_of_node_dict_to_groups_dict(groups_of_node_dict)
    print(len(groups_dict))

    # Ittération 
    while len(groups_dict) > 100:
        super_instance = createSuperInstance(instance, groups_of_node_dict, groups_dict)
        super_groups_of_node_dict = {node.get_idx(): node.get_idx() for node in super_instance.nodes}
        super_deg_of_comm_dict = {node.get_idx(): node.degree() for node in super_instance.nodes}
        super_groups_of_node_dict, super_deg_of_comm_dict, super_v = nodesShift(super_instance, super_groups_of_node_dict, super_deg_of_comm_dict)
        if super_v <= v + 0.00000001:
            break
        v = super_v
        groups_of_node_dict = retrieveSolFromSuperSol(instance, groups_of_node_dict, super_groups_of_node_dict, v)
        groups_dict = groups_of_node_dict_to_groups_dict(groups_of_node_dict)
        print(len(groups_dict), super_v)
        

    return groups_of_node_dict, v
    
def nodesShift(instance: Instance, groups_of_node_dict, deg_of_comm_dict):
        """
        Parcours les noeuds en modifiants la solution au voisins le plus optimal jusqu'à ce qu'il n'en trouve plus.
        """
        # Initialisation
        nodes = deque(instance.nodes)
        v = instance.solution_value(buildSolution(groups_of_node_dict))

        # Ittération
        stop = False
        while not stop:
            stop = True
            for n in instance.nodes:
                n_id = n.get_idx()
                n_neigh_id = n.neighbors()
                for neigh_id in n_neigh_id: 
                    n_c_id = groups_of_node_dict[n_id]
                    neigh_c_id = groups_of_node_dict[neigh_id]
                    if neigh_c_id != n_c_id:
                        new_v = v + modularityGain(instance, n, n_c_id, neigh_c_id, groups_of_node_dict, deg_of_comm_dict)
                        if new_v > v:
                            stop = False
                            deg_of_comm_dict[n_c_id] -= n.degree()
                            groups_of_node_dict[n_id] = neigh_c_id
                            v = new_v
                            deg_of_comm_dict[neigh_c_id] += n.degree()
        
        # Incrémentation correcte
        unique_groups = sorted(set(groups_of_node_dict.values()))
        mapping = {valeur: i+1 for i, valeur in enumerate(unique_groups)} 
        groups_of_node_dict = {k: mapping[v] for k, v in groups_of_node_dict.items()}

        return groups_of_node_dict, deg_of_comm_dict, v

    
def modularityGain(instance: Instance, n: Node, old_c: int, new_c: int, groups_of_node, deg_of_comm_dict):
        """
        Calcul rapidement le gain (positif ou négatif) de modularité par le passage du noeud n de la communautée old_c à new_c
        """
        # Initialisation
        dQ = 0
        n_id = n.get_idx()
        if instance.superGraphe:
            M = instance.realM
        else:
            M = instance.M

        # Etape 1
        d_n = n.degree()
        d_old_c = deg_of_comm_dict[old_c]
        d_new_c = deg_of_comm_dict[new_c]
        dQ += 2*d_n*(d_old_c - d_new_c - d_n)/((2*M)**2)

        # Etape 2
        d_link = 0
        for neigh_id in n.neighbors():
            if groups_of_node[neigh_id] == new_c:
                d_link += 2
            if neigh_id != n_id and groups_of_node[neigh_id] == old_c:
                d_link -= 2
        dQ += d_link/(2*M)

        return dQ

def buildSolution(groups_of_node_dict: dict) -> Solution:
    """
    Construit un objet solution à partir du groups_of_node
    """
    groups_dict = defaultdict(list)  
    for key, value in groups_of_node_dict.items():
        groups_dict[value].append(key)
    return Solution([v for v in groups_dict.values()])

def createSuperInstance(instance: Instance, groups_of_node_dict: dict, groups_dict: dict):
    """
        Créer l'instance du graphe agrégé'
        """
    # Initialisation
    nb_of_c = len(groups_dict)
    conectivity = {i+1: [] for i in range(nb_of_c)}
    
    # Inventaire des arretes
    m = 0 
    for e in instance.edges:
        n_i_id, n_j_id = e.get_idx()
        c_i_id = groups_of_node_dict[n_i_id]
        c_j_id = groups_of_node_dict[n_j_id]
        if c_i_id != c_j_id:
            m+=1
            conectivity[c_i_id].append(c_j_id)
            conectivity[c_j_id].append(c_i_id) 
 
        elif c_i_id == c_j_id:
            if n_i_id == n_j_id:
                m+=1
                conectivity[c_i_id].append(c_j_id)
            else:
                m+=2
                conectivity[c_i_id].append(c_j_id)
                conectivity[c_i_id].append(c_j_id)

    # Création du fichier txt
    with open("./instances/superGraphe", "w", encoding="utf-8") as fichier:
        fichier.write(f"{nb_of_c} {m}\n")
        for value in conectivity.values():
            fichier.write(" ".join(map(str, value))+"\n")

    # Creation de la super instance
    if instance.superGraphe:
        realM = instance.realM
    else:
        realM = instance.M
    super_instance = Instance("./instances/superGraphe", realM, True)
    

    return super_instance


def retrieveSolFromSuperSol(instance: Instance, groups_of_node_dict: dict, super_groups_of_node_dict: dict, v: float):
    """
        Recréer la solution de l'instance de base en aprtant de la solution de l'instance du graphe agrégé
        """
    groups_dict = groups_of_node_dict_to_groups_dict(groups_of_node_dict)
    super_groups_dict = groups_of_node_dict_to_groups_dict(super_groups_of_node_dict)
    for s_c in super_groups_dict.values():
        ref_nodes = [groups_dict[c_id][0] for c_id in s_c]
        for i in range(1,len(ref_nodes)):
            c_i_id = groups_of_node_dict[ref_nodes[0]]
            c_j_id = groups_of_node_dict[ref_nodes[i]]

            groups_of_node_dict, v = merge2Comm(instance, groups_of_node_dict, c_i_id, c_j_id, v)

    return groups_of_node_dict


def groups_of_node_dict_to_groups_dict(groups_of_node_dict: dict):
        """
        Créer le group_dict à partir du groups_of_node
        """
        groups_dict = {}
        for key, val in groups_of_node_dict.items():
            if val in groups_dict:
                groups_dict[val].append(key)
            else:
                groups_dict[val] = [key]
        return groups_dict



def merge2Comm(instance: Instance, groups_of_node_dict: dict, c_i_id: int, c_j_id: int, v: float):
    """
        Fusionne 2 communauté et calcule la valeur de la nouvelle solution
        """
    # Initialisation
    c_min_id = min(c_i_id, c_j_id)
    c_max_id = max(c_i_id, c_j_id)
    new_groups_of_node_dict = copy.deepcopy(groups_of_node_dict)
    new_groups_dict = groups_of_node_dict_to_groups_dict(new_groups_of_node_dict)
    c_min = new_groups_dict[c_min_id]
    c_max = new_groups_dict[c_max_id]
    L = max(new_groups_dict.keys())

    # Etape 1
    for n_id in c_max:
        new_groups_of_node_dict[n_id] = c_min_id

    # Etape 2
    del new_groups_dict[c_max_id]
    
    for i in range(c_max_id + 1, L + 1):
        new_groups_dict[i-1] =  new_groups_dict[i]
        for n_id in new_groups_dict[i-1]:
            new_groups_of_node_dict[n_id] -= 1
        del new_groups_dict[i]

    # Mise à jour de Q
    dQ = 0
    if instance.superGraphe:
        M = instance.realM
    else:
        M = instance.M

    # Etape 1
    d_min = 0
    d_max = 0
    for n_id in c_min:
        n = instance.nodes[n_id-1]
        d_min += n.degree()
    for n_id in c_max:
        n = instance.nodes[n_id-1]
        d_max += n.degree()    
    dQ -= 2*d_max*d_min/((2*M)**2)

    # Etape 2
    d_link = 0
    for n_id in c_min:
        n = instance.nodes[n_id-1]
        neighs_id = n.neighbors()
        for neigh_id in neighs_id:
            neigh_c_id = groups_of_node_dict[neigh_id]
            if neigh_c_id == c_max_id:
                d_link += 2

    dQ += d_link/(2*M)

    return new_groups_of_node_dict, v + dQ


def mergeKComm(instance: Instance, groups_of_node_dict: dict, v: float, k: int, V: int):
    """
        Génère V voisins et leurs valeur de modularité par la fusion de K communautés 
        """
    # Initialisation
    voisinages = []

    for _ in range(V):
        # Copie de solution
        new_groups_of_node_dict = copy.deepcopy(groups_of_node_dict)
        new_groups_dict = groups_of_node_dict_to_groups_dict(groups_of_node_dict)
        new_v = v
        # On essaye de faire k fusions aléatoire
        for l in range(k):
            # On fait 10 essais pour trouver une communauté ayant des communautés adjacentes
            inc = 0
            while inc < 10:
                # Choix d'une communauté
                c_i_id = rd.choice(list(new_groups_dict.keys()))
                c_i = new_groups_dict[c_i_id]
                # Calcul de ses communauté adjacentes
                c_i_neigh_id = []
                for n_id in c_i:
                    n = instance.nodes[n_id-1]
                    for neigh_id in n.neighbors():
                        c_neigh_id = new_groups_of_node_dict[neigh_id]
                        if c_neigh_id != c_i_id:
                            c_i_neigh_id.append(c_neigh_id)
                if len(c_i_neigh_id) == 0:
                    inc += 1
                else: 
                    break
            
            # Si on a trouvé, on choisis quelle communauté fusionner avec la première 
            if len(c_i_neigh_id) != 0:
                c_j_id = rd.choice(c_i_neigh_id)
            else: break
            # Création nouvelle solution et calcul valeur
            new_groups_of_node_dict, new_v = merge2Comm(instance, groups_of_node_dict, c_i_id, c_j_id, v)
        
        voisinages.append((new_groups_of_node_dict, new_v, "fusion"))
      
    return voisinages



def moveKNodes(instance: Instance, groups_of_node_dict: dict, v: float, k: int, V: int):
    """
        Génère V voisins et leurs valeur de modularité par déplacement K noeuds 
        """
    # Initialisation
    voisinages = []

    # CHANGEMENT DE COMMUNAUTEE POUR K NOEUD
    for _ in range(V):
        # Choix de noeuds à bouger
        nodes_to_move = rd.sample(instance.nodes, k)
        
        # On regarde où on peut les bouger
        list_of_possible_comm = [None for _ in range(k)]                    
        for i, n in enumerate(nodes_to_move):
            neighs_id = n.neighbors()
            list_of_possible_comm[i] = Counter([groups_of_node_dict[neigh_id] for neigh_id in neighs_id])
        # On choisis une combinaison de mouvement
        combinaisons = list(itertools.product(*list_of_possible_comm))

        # Sauvegarde de la meilleure combinaisons actuelle
        best_groups_of_node_dict = copy.deepcopy(groups_of_node_dict)
        best_v = v

        # Génération de toute les combinaisons
        for combinaison in combinaisons:
            # Test de validité de la combinaison
            valid = True
            for i, c_i in enumerate(combinaison):
                if list_of_possible_comm[i][c_i] <= 0:
                    valid = False #TODO On sort de la boucle mais en vrai la validité pourrait revenir si on continue
                    break
                n_i = nodes_to_move[i]
                n_i_idx = n_i.get_idx()
                n_i_curr_group = groups_of_node_dict[n_i_idx]
                n_i_neighs_id = n_i.neighbors()
                
                for j, n in enumerate(nodes_to_move):
                    n_id = n.get_idx()
                    if n_id in n_i_neighs_id:
                        list_of_possible_comm[j][n_i_curr_group] -= 1
                        if c_i in list_of_possible_comm[j]: list_of_possible_comm[j][c_i] += 1
                        else: list_of_possible_comm[j][c_i] = 1
            
            # Changement de la solution et de sa valeur
            if valid:
                local_groups_of_node_dict, local_v = copy.deepcopy(groups_of_node_dict), v
                for i, c_id in enumerate(combinaison):
                    local_groups_dict = groups_of_node_dict_to_groups_dict(local_groups_of_node_dict)
                    n_i = nodes_to_move[i]
                    n_i_id = n_i.get_idx()
                    n_i_c_id = local_groups_of_node_dict[n_i_id]
                    # Recalage des indices si nécéssaires
                    if(len(local_groups_dict[n_i_c_id]) <= 1):
                        for j in range(i+1,len(combinaison)):
                            if combinaison[j] >= local_groups_of_node_dict[n_i_id]:
                                combinaison[j] -= 1

                    # Modification
                    local_groups_of_node_dict, local_v = modifyOneNode(instance, local_groups_of_node_dict, n_i, n_i_c_id, c_id, local_v)
                    # On garde la meilleure
                    if local_v > best_v:
                        best_groups_of_node_dict = copy.deepcopy(local_groups_of_node_dict)
                        best_v = local_v

        voisinages.append((best_groups_of_node_dict, best_v, "mouvement"))

    return voisinages



def modifyOneNode(instance: Instance, groups_of_node_dict: dict, n: Node, old_c_id: int, new_c_id: int, v: float):
    """
        Déplace 1 noeud et calcule la valeur de la nouvelle solution
        """
    # Initialisation
    n_id = n.get_idx()
    n_neigh = n.neighbors()
    new_groups_of_node_dict = copy.deepcopy(groups_of_node_dict)
    new_groups_of_dict = groups_of_node_dict_to_groups_dict(new_groups_of_node_dict)
    old_c = new_groups_of_dict[old_c_id]
    new_c = new_groups_of_dict[new_c_id]
    

    # Modification de la solution
    new_groups_of_node_dict[n_id] = new_c_id

    # Incrémentation correcte
    unique_groups = sorted(set(new_groups_of_node_dict.values()))
    mapping = {valeur: i+1 for i, valeur in enumerate(unique_groups)} 
    new_groups_of_node_dict = {k: mapping[v] for k, v in new_groups_of_node_dict.items()}

    # Mise à jour de Q
    dQ = 0
    if instance.superGraphe:
        M = instance.realM
    else:
        M = instance.M

    # Etape 1
    d_n = n.degree()
    d_old_c = 0
    d_new_c = 0
    
    if old_c_id != new_c_id:
        for n_id in old_c:
            n = instance.nodes[n_id-1]
            d_old_c += n.degree()
        for n_id in new_c:
            n = instance.nodes[n_id-1]
            d_new_c += n.degree()    

        dQ += 2*d_n*(d_old_c - d_new_c - d_n)/((2*M)**2)

    # Etape 2
    d_link = 0
    for neigh_id in n_neigh:
        if groups_of_node_dict[neigh_id] == new_c_id:
            d_link += 2
        if groups_of_node_dict[neigh_id] == old_c_id:
            d_link -= 2

    dQ += d_link/(2*M)
    return new_groups_of_node_dict, v + dQ