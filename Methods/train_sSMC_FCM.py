import pandas as pd
import sklearn, os, json, numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, normalize
import sqlite3, pickle
import collections
from sSMC_FCM_method import sSMC_FCM


basedir = os.path.dirname(os.path.dirname(__file__))
results_path = os.path.join(basedir, 'Coauthor_Candidate_Tables')
clusters_path = os.path.join(basedir, 'Clustering_Results')
db_path = os.path.join(basedir, 'Database')


def train(data_name,m,m1,eps,l):
    # Normalize filename: remove .csv if present, will add back at the end
    if data_name.lower().endswith('.csv'):
        data_name = data_name[:-4]
    
    if not data_name:
        raise ValueError('Tệp dữ liệu không hợp lệ.')

    # Add .csv back for file path
    data_name_with_ext = data_name + '.csv'
    data_path = os.path.join(results_path, data_name_with_ext)
    if not os.path.isfile(data_path):
        raise FileNotFoundError(f"Không tìm thấy tệp dữ liệu: {data_name_with_ext}. Vui lòng chọn tệp trong Coauthor_Candidate_Tables.")

    m = int(m)
    m1 = int(m1)
    eps = float(eps)
    l = int(l)
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
    output_filename = "sSMCFCM_" + data_name + ".csv"
    output_path = os.path.join(clusters_path, output_filename)
    if os.path.exists(output_path):
        result.to_csv(output_path, index=False)
        print(f"Kết quả đã được ghi đè lên '{output_filename}'.")
    else:
        result.to_csv(output_path, index=False)
    
    return {
        "cluster_center": center_label[0].tolist(),
        "input_file": data_name_with_ext,
        "output_file": output_filename,
        "output_path": "Clustering_Results",
        "status": "success",
        "message": f"Huấn luyện thành công. File kết quả: {output_filename}"
    }


    

