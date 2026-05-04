from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from train_sSMC_FCM import train
from recommend import recommend
import os
from query import get_all_authors

app = Flask(__name__)
CORS(app)

basedir = os.path.dirname((os.path.dirname(__file__)))
results_path = os.path.join(basedir, 'D:/DATA/23A-IT-KHMT- BKHN/Kì 2 - 2022-2023/DADX/CODE/CoAuthor-Recommendation/Coauthor_Candidate_Tables')
@app.route('/')
def _index():
    return render_template('train_recommend_sSMC_FCM.html')
    

@app.route('/train', methods=['POST'])
def _train():
    data_name = request.get_json()["data_name"]
    m = request.get_json()["m"]
    m1 = request.get_json()["m1"]
    eps = request.get_json()["eps"]
    l = request.get_json()["l"]
    return train(data_name, m, m1, eps, l)

@app.route('/recommend', methods=['POST'])
def _recommend():
    author_id = request.get_json()['author_id']
    table_name = request.get_json()['table_name']
    cluster_center = request.get_json()['cluster_center']
    return recommend(author_id, table_name, cluster_center)

@app.route('/get_all_authors', methods=['POST'])
def _get_all_authors():
    data_name = request.get_json()["data_name"]
    return get_all_authors(data_name)

app.run(debug=True, host='127.0.0.1', port=5002)