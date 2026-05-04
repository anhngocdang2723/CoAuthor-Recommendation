import pandas as pd
import sklearn, os, json, numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, normalize
import sqlite3, pickle
import collections
from sSMC_FCM_method import sSMC_FCM


basedir = os.path.dirname((os.path.dirname(__file__)))
results_path = os.path.join(basedir, 'D:/DATA/23A-IT-KHMT- BKHN/Kì 2 - 2022-2023/DADX/CODE/CoAuthor-Recommendation/Coauthor_Candidate_Tables')
clusters_path = os.path.join(basedir, 'D:/DATA/23A-IT-KHMT- BKHN/Kì 2 - 2022-2023/DADX/CODE/CoAuthor-Recommendation/Clustering_Results')
db_path = os.path.join(os.path.dirname(basedir), 'D:/DATA/23A-IT-KHMT- BKHN/Kì 2 - 2022-2023/DADX/CODE/CoAuthor-Recommendation/Database')


def train(data_name,m,m1,eps,l):
    m = int(m)
    m1 = int(m1)
    eps = float(eps)
    l = int(l)
    data_path = results_path + "/" + data_name
    data = pd.read_csv(data_path)
    # print(data.shape)

    X = data.drop(columns=['id_author_1', 'id_author_2', 'Label'])
    y = data['Label']
    X = np.array(X)
    y = np.array(y)
    print(X.shape)
    print("Tỉ lệ nhãn -1-1")
    print(np.sum(y==-1), end='--')
    print(np.sum(y==1))

    scaler = MinMaxScaler().fit(X)
    X = scaler.transform(X)
    
    model = sSMC_FCM()
    model.preprocess_data(X,y)
    membership_matrix, center_label = model.clusering_sSMC_FCM(m,m1,eps,l)
    print(center_label)
    label = model.assign_label()
    label_name = "cluster_id"
    label_df = pd.DataFrame({label_name: label})
    result = pd.concat([data, label_df], axis=1)
    print(result)

    # Lưu kết quả vào file CSV
    output_path = clusters_path + "/" + "sSMCFCM_" + data_name
    if os.path.exists(output_path):
        result.to_csv(output_path, index=False)
        print(f"Kết quả đã được ghi đè lên '{data_name}'.")
    else:
        result.to_csv(output_path, index=False)
    
    return json.dumps({"cluster_center":center_label[0].tolist(),"table_name": data_name})


    

