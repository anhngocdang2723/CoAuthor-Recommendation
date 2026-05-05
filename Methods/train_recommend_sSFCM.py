from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from train_sSFCM import train
from recommend import recommend
import os
import json
from query import get_all_authors

app = Flask(__name__)
CORS(app)

basedir = os.path.dirname(os.path.dirname(__file__))
results_path = os.path.join(basedir, 'Coauthor_Candidate_Tables')
@app.route('/')
def _index():
    return render_template('train_recommend_sSFCM.html')
    

@app.route('/train', methods=['POST'])
def _train():
    payload = request.get_json(silent=True) or {}
    data_name = payload.get("data_name")
    m = payload.get("m")
    eps = payload.get("eps")
    l = payload.get("l")

    if not data_name or m is None or eps is None or l is None:
        return jsonify({"error": "Thiếu dữ liệu đầu vào cho huấn luyện."}), 400

    try:
        result = train(data_name, m, eps, l)
        return jsonify(result)
    except FileNotFoundError as error:
        return jsonify({"error": str(error)}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Lỗi hệ thống khi huấn luyện: {error}"}), 500

@app.route('/get_all_authors', methods=['POST'])
def _get_all_authors():
    payload = request.get_json(silent=True) or {}
    data_name = payload.get("data_name")
    if not data_name:
        return jsonify({"error": "Thiếu data_name."}), 400
    try:
        result = get_all_authors(data_name)
        if isinstance(result, str):
            return jsonify(json.loads(result))
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": f"Lỗi khi lấy danh sách tác giả: {error}"}), 500


@app.route('/recommend', methods=['POST'])
def _recommend():
    payload = request.get_json(silent=True) or {}
    author_id = payload.get('author_id')
    table_name = payload.get('table_name')
    cluster_center = payload.get('cluster_center')

    if author_id is None or not table_name:
        return jsonify({"error": "Thiếu author_id hoặc table_name."}), 400
    if cluster_center is None:
        return jsonify({"error": "Thiếu cluster_center. Vui lòng huấn luyện trước khi gợi ý."}), 400

    try:
        result = recommend(author_id, table_name, cluster_center)
        if isinstance(result, str):
            return jsonify(json.loads(result))
        return jsonify(result)
    except FileNotFoundError as error:
        return jsonify({"error": str(error)}), 400
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        return jsonify({"error": f"Lỗi hệ thống khi gợi ý: {error}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)