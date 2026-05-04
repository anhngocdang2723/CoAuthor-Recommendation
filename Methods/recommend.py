import sqlite3, json, os, pickle
from query import *
from co_author_graph import *
from define_scores import *
import numpy as np
from collections import defaultdict
import pandas as pd
from train_sSFCM import *

basedir = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))
db_path = os.path.join(basedir, 'D:/DATA/23A-IT-KHMT- BKHN/Kì 2 - 2022-2023/DADX/CODE/CoAuthor-Recommendation/Database')
clusters_path = os.path.join(basedir, 'D:/DATA/23A-IT-KHMT- BKHN/Kì 2 - 2022-2023/DADX/CODE/CoAuthor-Recommendation/Clustering_Results')


def create_sub_db(topic, from_date, to_date):
    # _ = create_sub_tables([topic], from_date, to_date)
    sub_db_name = "subDB_" + topic + "_" + from_date + "_" + to_date
    return sub_db_name

def create_co_author_table(topic, from_date, to_date):
    _ = create_co_authors([topic], from_date, to_date)

def get_co_author(id, sub_db_name):   # find co authors of ONLY one author to save memory
    with sqlite3.connect(db_path + '/' + sub_db_name + ".sqlite3") as conn:
        cur = conn.cursor()
        query = ("select distinct pa.author_id from paper_authors pa \
                  where pa.paper_id in \
                  (select paper_id from paper_authors \
                   where author_id = " + str(id) + ") \
                  and pa.author_id != " + str(id)
                )
        cur.execute(query)
        co_authors = cur.fetchall()
        return co_authors
    
def get_potential(id, adj, sub_db_name):  # this could be extended to find candidates by affiliation
    potential = set()
    co_authors = list(adj[id].keys())
    for u in co_authors:
        u_co_authors = list(adj[u].keys())
        for v in u_co_authors:
            if v in co_authors or v == id:
                continue
            potential.add(v)
    result = []  # find candidates with same country_id
    with sqlite3.connect(db_path + '/' + sub_db_name + ".sqlite3") as conn:
        conn.row_factory = lambda cursor, row: row[0]
        cur = conn.cursor()
        query = ("select id from author \
                  where country_id = (select country_id from author where id = " + str(id) + ") \
                ")
        cur.execute(query)
        result = cur.fetchall()
        result = [i for i in result if i not in co_authors]
    for i in result:
        potential.add(i)
    return potential

# def recommend(topic, from_date, to_date, author_id, model_name):
#     list_recommend = defaultdict(int)
#     # print("Creating sub network")
#     sub_db_name = create_sub_db(topic, from_date, to_date)
#     # print("Sub network created")
#     create_co_author_table(topic, from_date, to_date)
#     print("Creating co author network...")
#     graph = Co_Author_Graph(db_path + '/' + sub_db_name + ".sqlite3")
#     print("Co author network created")
#     adj = graph.adj
#     if author_id in adj:
#         potential = get_potential(author_id, adj, sub_db_name)   # get candidates from network links
#         scores = dict()
#         # print("id:", author_id)
#         # print("Potential:", potential)
#         co_id = list(adj[author_id].keys())
#         t = max(graph.time_patterns) + 1
#         for u in potential:
#             co_u = list(adj[u].keys())
#             common_neighbors = list(set(co_id) & set(co_u))
#             weight_type = "unweighted"
#             cm = CommonNeighbor(author_id, u, adj, t, co_id, co_u, common_neighbors, weight_type)
#             aa = AdamicAdar(author_id, u, adj, t, co_id, co_u, common_neighbors, weight_type)
#             jc = JaccardCoefficient(author_id, u, adj, t, co_id, co_u, common_neighbors, weight_type)
#             pa = PreferentialAttachment(author_id, u, adj, t, co_id, co_u, common_neighbors, weight_type)
#             ra = ResourceAllocation(author_id, u, adj, t, co_id, co_u, common_neighbors, weight_type)
#             sp = ShortestPath(author_id, u, adj, t)
#             cc = CommonCountry_pair(author_id, u, graph.list_vertices, common_neighbors)
#             score = np.array([cm,aa,jc,pa,ra,sp,cc])
#             scores[u] = score

#         X = np.array(list(scores.values()))
#         print(X)
#         tmp = model_name.split("_")
#         tmp[0] = "Scaler"
#         scaler_name = "_".join(tmp)
#         print(scaler_name)
#         # print(X)
#         # print("-------------")
#         # with open(models_path + '/' + scaler_name, 'rb') as file:
#         #     scaler = pickle.load(file)
#         #     X = scaler.transform(X)


#         # print(X)
#         with open(models_path + '/' + model_name, 'rb') as file:
#             model = pickle.load(file)
#             y = model.predict(X)
#             print(y)
#             for idx,u in enumerate(potential):
#                 if y[idx] == 1:
#                     list_recommend[u] = np.mean(X[idx])
#         list_recommend = dict(sorted(list_recommend.items(), key=lambda item: item[1], reverse=True))
#         print(list_recommend)
#         # get name of candidates
#         result = get_all_authors(topic, from_date, to_date)
#         records = json.loads(result)
#         mapping = {}
#         for idx in range(len(records['id'])):
#             mapping[int(records['id'][idx])] = records["first_name"][idx] + " " + records["last_name"][idx] 
#         list_name = []
#         for cand in list_recommend.keys():
#             list_name.append(mapping[cand])
#         return json.dumps({"potential": list(list_recommend.keys()), 'name': list_name, 'score': list(list_recommend.values())})
#     else:
#         return json.dumps({"potential": "Invalid author"})

def recommend(author_id, table_name,cluster_center):
    list_recommend = defaultdict(int)
    print(cluster_center)
    print(table_name)
    data_path = clusters_path + "/" + table_name
    data = pd.read_csv(data_path)

    y = data['cluster_id']
    y = np.array(y)
    X = data.drop(columns=['id_author_1', 'id_author_2', 'Label','cluster_id'])
    X = np.array(X)
    data = np.array(data)
    
    for i in range(len(data)):
        if (author_id == data[i][0] and y[i]==1):
            list_recommend[data[i][1]] = np.linalg.norm(X[i] - cluster_center)
        if (author_id == data[i][1] and y[i]==1):
            list_recommend[data[i][0]] = np.linalg.norm(X[i] - cluster_center)

    list_recommend = dict(sorted(list_recommend.items(), key=lambda item: item[1]))
    print(list_recommend)
    # get name of candidates
    result = get_all_authors(table_name)
    records = json.loads(result)
    mapping = {}
    for idx in range(len(records['id'])):
        mapping[int(records['id'][idx])] = records["first_name"][idx] + " " + records["last_name"][idx] 
    list_name = []
    for cand in list_recommend.keys():
        list_name.append(mapping[cand])
    return json.dumps({"potential": list(list_recommend.keys()), 'name': list_name, 'score': list(list_recommend.values())})

        


        
    

