from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
from collections import defaultdict
import math
import csv
import pandas as pd
import json, os

from calculate_scores import calculate_scores_dynamic, calculate_scores_static
from query import create_sub_tables, create_co_authors, create_potential_co_authors, get_dates_of_topics
from co_author_graph import *

app = Flask(__name__)
CORS(app)

# direct path of database
# db_path = "/home/lam/Documents/prj3_copy/prj3/data/db.sqlite3"
basedir = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))
db_path = os.path.join(basedir, 'D:/DATA/CS-MASTER-HUST/2022_2023_2/DADX/CODE/CoAuthor-Recommendation/Database') 
@app.route('/')
def _index():
    return render_template('bootstrap_template.html')

@app.route('/get_dates_of_topics', methods=['POST'])
def _get_dates_of_topics():
    topics = request.get_json()["topics"]
    return get_dates_of_topics(topics)

@app.route('/query', methods=['POST'])
def _query():
    topics = request.get_json()["topics"]
    from_date = request.get_json()["from_date"]
    to_date = request.get_json()["to_date"]
    return create_sub_tables(topics, from_date, to_date)
    

@app.route('/create_co_authors', methods=['POST'])
def _create_co_authors():
    topics = request.get_json()["topics"]
    from_date = request.get_json()["from_date"]
    to_date = request.get_json()["to_date"]
    return create_co_authors(topics, from_date, to_date)


@app.route('/create_potential_co_authors', methods=['POST'])
def _create_potential_co_authors():
    # level = request.get_json()["level"]
    topics = request.get_json()["topics"]
    from_date = request.get_json()["from_date"]
    to_date = request.get_json()["to_date"]
    return create_potential_co_authors(topics, "co_author", "potential_co_author_", from_date, to_date)
    
   
@app.route('/calculate_scores', methods=['POST'])
def _calculate_scores():
    # time is divided by year
    # level = request.get_json()["level"]
    topics = request.get_json()["topics"]
    # weight_type = request.get_json()["weight_type"]
    # label_type = request.get_json()["label_type"]
    from_date = request.get_json()["from_date"]
    to_date = request.get_json()["to_date"]
    csv_file_name = request.get_json()["csv_file_name"]
    graph = Co_Author_Graph(db_path + "/subDB_" + "".join(topics) + "_" + from_date + "_" + to_date + ".sqlite3")
    # if label_type == "dynamic":
    #     return calculate_scores_dynamic(topics, from_date, to_date, weight_type, graph, csv_file_name)
    # if label_type == "static":
    time_slice = request.get_json()["time_slice"]
    return calculate_scores_static(topics, from_date, to_date, graph, time_slice, csv_file_name)


app.run(debug=True, host='127.0.0.1', port=5000)
