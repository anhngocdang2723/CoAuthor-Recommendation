import math

def list_co_authors_before_t(u, t, adj):
    res = []    
    for v in adj[u].keys():
        for year in adj[u][v].years.keys():
            if year < t:
                res.append(v)
                break
    return res

def get_weight_before_t(u,v,adj,t):
    old_w = adj[u][v].w
    cnt = 0
    for year in sorted(adj[u][v].years.keys(), reverse=True):
        if year >= t: 
            cnt += adj[u][v].years[year]
        else: break
    return old_w - cnt

def CommonNeighbor(id1, id2, adj, t, co_id1, co_id2, common_neighbors, weight_type):
    # co_id1 = list_co_authors_before_t(id1, t, adj)
    # co_id2 = list_co_authors_before_t(id2, t, adj)
    # common_neighbors = list(set(co_id1) & set(co_id2))
    res = 0
    if weight_type == "unweighted":
        res = len(common_neighbors)
    else:
        for z in common_neighbors:
            w_id1_z = get_weight_before_t(id1, z, adj, t)
            w_id2_z = get_weight_before_t(id2, z, adj, t)
            res += (w_id1_z + w_id2_z) / 2
    return res

def AdamicAdar(id1, id2, adj, t, co_id1, co_id2, common_neighbors, weight_type):
    # {z}
    # co_id1 = list_co_authors_before_t(id1, t, adj)
    # co_id2 = list_co_authors_before_t(id2, t, adj)
    # common_neighbors = list(set(co_id1) & set(co_id2))
    res = 0
    if weight_type == "unweighted":
        for z in common_neighbors:
            co_z = list_co_authors_before_t(z, t, adj)
            if len(co_z) > 1:
                res += 1 / (math.log(len(co_z)))
    else:
        for z in common_neighbors:
            w_id1_z = get_weight_before_t(id1, z, adj, t)
            w_id2_z = get_weight_before_t(id2, z, adj, t)
            numerator = (w_id1_z + w_id2_z) / 2
            denominator = 0
            co_z = list_co_authors_before_t(z, t, adj)
            for i in co_z:
                w_z_i = get_weight_before_t(z, i, adj, t)
                denominator += w_z_i
            if denominator > 1:
                denominator = math.log(denominator)
                res += numerator / denominator
    return res

def JaccardCoefficient(id1, id2, adj, t, co_id1, co_id2, common_neighbors, weight_type):
    # co_id1 = list_co_authors_before_t(id1, t, adj)
    # co_id2 = list_co_authors_before_t(id2, t, adj)
    res = 0
    if weight_type == "unweighted":
        if len(co_id1) > 0 or len(co_id2) > 0: 
            res = len(common_neighbors) / len(set(co_id1).union(set(co_id2)))
    else:   # same
        if len(co_id1) > 0 or len(co_id2) > 0: 
            res = len(common_neighbors) / len(set(co_id1).union(set(co_id2)))
    return res

def PreferentialAttachment(id1, id2, adj, t, co_id1, co_id2, common_neighbors, weight_type):
    # co_id1 = list_co_authors_before_t(id1, t, adj)
    # co_id2 = list_co_authors_before_t(id2, t, adj)
    res = 0
    if weight_type == "unweighted":
        res = len(co_id1) * len(co_id2)
    else:
        id1_contri = 0
        for z in co_id1:
            w_id1_z = get_weight_before_t(id1, z, adj, t)
            id1_contri += w_id1_z
        if len(co_id1) > 0: 
            id1_contri /= len(co_id1)

        id2_contri = 0
        for z in co_id2:
            w_id2_z = get_weight_before_t(id2, z, adj, t)
            id2_contri += w_id2_z
        if len(co_id2)> 0:
            id2_contri /= len(co_id2)
            
        res = id1_contri * id2_contri

    return res

def ResourceAllocation(id1, id2, adj, t, co_id1, co_id2, common_neighbors, weight_type):
    # {z}
    # co_id1 = list_co_authors_before_t(id1, t, adj)
    # co_id2 = list_co_authors_before_t(id2, t, adj)
    # common_neighbors = list(set(co_id1) & set(co_id2))
    res = 0
    if weight_type == "unweighted":
        for z in common_neighbors:
            co_z = list_co_authors_before_t(z, t, adj)
            if len(co_z) > 0:
                res += 1 / (len(co_z))
    else:
        for z in common_neighbors:
            w_id1_z = get_weight_before_t(id1, z, adj, t)
            w_id2_z = get_weight_before_t(id2, z, adj, t)
            numerator = (w_id1_z + w_id2_z) / 2
            co_z = list_co_authors_before_t(z, t, adj)
            denominator = 0
            for i in co_z:
                w_z_i = get_weight_before_t(z, i, adj, t)
                denominator += w_z_i
            if denominator > 0:
                res += numerator / denominator
    return res

def bfs(s, e, adj, t):     #bfs to find shortest path between s and e  ==> Time complexity
    num_ver = len(adj)
    max_num_edges = num_ver * (num_ver-1) / 2
    if s == e: return 0
    visited = dict.fromkeys(adj.keys(), False)
    dist = dict.fromkeys(adj.keys(), max_num_edges)
    q = []
    q.append(s)
    visited[s] = True
    dist[s] = 0
    while q:
        u = q.pop(0)
        co_u = list_co_authors_before_t(u, t, adj)
        if u == e: return dist[u]
        else:
            for v in co_u:
                if visited[v] == False:
                    q.append(v)
                    visited[v] = True  
                    dist[v] = dist[u] + 1
    return 0

def bidirectional_shortest_path(adj, source, target, t):
    if bidirectional_pred_succ(adj, source, target, t) is None:
        return [1]
    else:
        pred, succ, w = bidirectional_pred_succ(adj, source, target, t)
        path = []
        while w is not None:
            path.append(w)
            w = pred[w]
        path.reverse()
        w = succ[path[-1]]
        while w is not None:
            path.append(w)
            w = succ[w]
        return path

def bidirectional_pred_succ(adj, source, target, t):
    Gpred = adj
    Gsucc = adj
    pred = {source: None}
    succ = {target: None}
    forward_fringe = [source]
    reverse_fringe = [target]
    while forward_fringe and reverse_fringe:
        if len(forward_fringe) <= len(reverse_fringe):
            this_level = forward_fringe
            forward_fringe = []
            for v in this_level:
                co_v = list_co_authors_before_t(v, t, adj)
                for w in co_v:
                    if w not in pred:
                        forward_fringe.append(w)
                        pred[w] = v
                    if w in succ:
                        return pred, succ, w
        else:
            this_level = reverse_fringe
            reverse_fringe = []
            for v in this_level:
                co_v = list_co_authors_before_t(v, t, adj)
                for w in co_v:
                    if w not in succ:
                        succ[w] = v
                        reverse_fringe.append(w)
                    if w in pred:
                        return pred, succ, w

def ShortestPath(id1, id2, adj,t):    # not take w into account
    dist = len(bidirectional_shortest_path(adj, id1,id2, t))-1
    if dist == 0: return 0
    else:   
        return 1 / dist


def CommonCountry_pair(id1, id2, list_vertices, common_neighbors):
    def sim_work_2(id1, id2):
        if list_vertices[id1].university == list_vertices[id2].university: return 2
        elif list_vertices[id1].country_id == list_vertices[id2].country_id: return 1
        else: return  0
    def sim_work_3(id1, id2, id3):
        if list_vertices[id1].university == list_vertices[id2].university and list_vertices[id1].university == list_vertices[id3].university:
            return 2
        elif list_vertices[id1].country_id == list_vertices[id2].country_id and list_vertices[id1].country_id == list_vertices[id3].country_id:
            return 1
        else: return 0

    comm_country_score = sim_work_2(id1, id2)    
    for z in common_neighbors:
        comm_country_score += sim_work_3(id1, id2, z)
    return comm_country_score

def CommonCountry(adj, list_vertices, records, max_time, label_type, time_slice):  # records of potential_co_author
    # return list of scores of each pair
    CommonCountry_list = []
    
    # query country_id and affiliation_id of 2 authors
        
    def sim_work_2(id1, id2):
        if list_vertices[id1].university == list_vertices[id2].university: return 2
        elif list_vertices[id1].country_id == list_vertices[id2].country_id: return 1
        else: return  0

    def sim_work_3(id1, id2, id3):
        if list_vertices[id1].university == list_vertices[id2].university and list_vertices[id1].university == list_vertices[id3].university:
            return 2
        elif list_vertices[id1].country_id == list_vertices[id2].country_id and list_vertices[id1].country_id == list_vertices[id3].country_id:
            return 1
        else: return 0

    if label_type == "dynamic":
        for row in records:
            id1 = row[0]
            id2 = row[1]
            if id2 in adj[id1].keys(): 
                t = adj[id1][id2].max_time_pattern
                comm_country_score = sim_work_2(id1, id2)    
                co_id1 = list_co_authors_before_t(id1, t, adj)
                co_id2 = list_co_authors_before_t(id2, t, adj)
                common_neighbors = list(set(co_id1) & set(co_id2))
                for z in common_neighbors:
                    comm_country_score += sim_work_3(id1, id2, z)
                CommonCountry_list.append(comm_country_score)
            else:
                comm_country_score = sim_work_2(id1, id2)    
                co_id1 = list_co_authors_before_t(id1, max_time, adj)
                co_id2 = list_co_authors_before_t(id2, max_time, adj)
                common_neighbors = list(set(co_id1) & set(co_id2))
                for z in common_neighbors:
                    comm_country_score += sim_work_3(id1, id2, z)
                CommonCountry_list.append(comm_country_score)
    if label_type == "static":
        for row in records:
            id1 = row[0]
            id2 = row[1]
            comm_country_score = sim_work_2(id1, id2)    
            co_id1 = list_co_authors_before_t(id1, time_slice, adj)
            co_id2 = list_co_authors_before_t(id2, time_slice, adj)
            common_neighbors = list(set(co_id1) & set(co_id2))
            for z in common_neighbors:
                comm_country_score += sim_work_3(id1, id2, z)
            CommonCountry_list.append(comm_country_score)
            
    return CommonCountry_list


