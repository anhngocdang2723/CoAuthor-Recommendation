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
basedir = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'Database') 


def _get_payload():
    payload = request.get_json(silent=True)
    if payload is None:
        return {}
    return payload


def _error(message, status_code=400):
    return jsonify({"error": message}), status_code


def _normalize_result(result):
    if isinstance(result, (dict, list)):
        return jsonify(result)
    if isinstance(result, str):
        try:
            return jsonify(json.loads(result))
        except json.JSONDecodeError:
            return jsonify({"message": result})
    return jsonify(result)


@app.route('/')
def _index():
    return render_template('bootstrap_template.html')

@app.route('/get_dates_of_topics', methods=['POST'])
def _get_dates_of_topics():
    payload = _get_payload()
    topics = payload.get("topics")
    if not topics:
        return _error("Thiếu danh sách chủ đề (topics).")
    try:
        return _normalize_result(get_dates_of_topics(topics))
    except Exception as error:
        return _error(f"Lỗi khi lấy khoảng năm theo chủ đề: {error}", 500)

@app.route('/query', methods=['POST'])
def _query():
    payload = _get_payload()
    topics = payload.get("topics")
    from_date = payload.get("from_date")
    to_date = payload.get("to_date")
    if not topics or not from_date or not to_date:
        return _error("Thiếu dữ liệu đầu vào: topics, from_date, to_date.")
    try:
        return _normalize_result(create_sub_tables(topics, str(from_date), str(to_date)))
    except Exception as error:
        return _error(f"Lỗi khi truy vấn dữ liệu: {error}", 500)
    

@app.route('/create_co_authors', methods=['POST'])
def _create_co_authors():
    payload = _get_payload()
    topics = payload.get("topics")
    from_date = payload.get("from_date")
    to_date = payload.get("to_date")
    if not topics or not from_date or not to_date:
        return _error("Thiếu dữ liệu đầu vào: topics, from_date, to_date.")
    try:
        return _normalize_result(create_co_authors(topics, str(from_date), str(to_date)))
    except Exception as error:
        return _error(f"Lỗi khi tạo bảng đồng tác giả: {error}", 500)


@app.route('/create_potential_co_authors', methods=['POST'])
def _create_potential_co_authors():
    # level = request.get_json()["level"]
    payload = _get_payload()
    topics = payload.get("topics")
    from_date = payload.get("from_date")
    to_date = payload.get("to_date")
    if not topics or not from_date or not to_date:
        return _error("Thiếu dữ liệu đầu vào: topics, from_date, to_date.")
    try:
        return _normalize_result(create_potential_co_authors(topics, "co_author", "potential_co_author_", str(from_date), str(to_date)))
    except Exception as error:
        return _error(f"Lỗi khi tạo bảng đồng tác giả tiềm năng: {error}", 500)
    
   
@app.route('/calculate_scores', methods=['POST'])
def _calculate_scores():
    # time is divided by year
    # level = request.get_json()["level"]
    payload = _get_payload()
    topics = payload.get("topics")
    # weight_type = request.get_json()["weight_type"]
    # label_type = request.get_json()["label_type"]
    from_date = payload.get("from_date")
    to_date = payload.get("to_date")
    time_slice = payload.get("time_slice")
    csv_file_name = payload.get("csv_file_name", "")

    if not topics or not from_date or not to_date:
        return _error("Thiếu dữ liệu đầu vào: topics, from_date, to_date.")
    if not time_slice:
        return _error("Thiếu time_slice. Vui lòng nhập lát cắt thời gian.")

    sub_db_file = os.path.join(db_path, f"subDB_{''.join(topics)}_{from_date}_{to_date}.sqlite3")
    if not os.path.isfile(sub_db_file):
        return _error("Không tìm thấy sub database. Hãy chạy truy vấn và tạo bảng trước khi tính điểm.")

    try:
        graph = Co_Author_Graph(sub_db_file)
    # if label_type == "dynamic":
    #     return calculate_scores_dynamic(topics, from_date, to_date, weight_type, graph, csv_file_name)
    # if label_type == "static":
        result = calculate_scores_static(topics, str(from_date), str(to_date), graph, str(time_slice), str(csv_file_name))
        return _normalize_result(result)
    except Exception as error:
        return _error(f"Lỗi khi tính điểm: {error}", 500)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
