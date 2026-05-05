import sqlite3
import json, os
import numpy as np

basedir = os.path.dirname(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'Database')

def get_dates_of_topics(topics):
    with sqlite3.connect(db_path + '/db.sqlite3') as conn:
        cur = conn.cursor()
        get_dates_query = ("select distinct p.date from collab_paper p \
                            where p.journal_id in (" + ','.join(topics) + ")")
        cur.execute(get_dates_query)
        records = cur.fetchall()
        # consider only years
        years = set()
        for date in records:
            date = date[0]
            year = int(date[0:4])
            years.add(year)
    return  json.dumps({"dates": sorted(list(years))})

def create_sub_tables(topics, from_date, to_date):
    topic_name = "".join(topics)
    with sqlite3.connect(db_path + '/db.sqlite3') as conn:
        cur = conn.cursor()
        cur.execute("ATTACH DATABASE '" + db_path +  "/subDB_" + topic_name + "_" + from_date + "_" + to_date + ".sqlite3' AS sub_db")
        name1 = "paper"
        name2 = "paper_authors"
        name3 = "author" 
        check_paper = "select count(name) from sub_db.sqlite_master where type='table' and name='paper'"
        check_paper_author = "select count(name) from sub_db.sqlite_master where type='table' and name='paper_authors'"
        check_author = "select count(name) from sub_db.sqlite_master where type='table' and name='author'"
        
        create_paper_table = ("create table sub_db.paper" +  
                            " as select p.id, p.date from collab_paper p \
                            where p.journal_id in (" + ','.join(topics) + ") \
                            and substr(p.date,1,4) >= '" + from_date + "' \
                            and substr(p.date,1,4) <= '" + to_date + "'"
                            )

        create_paper_authors_table = ("create table sub_db.paper_authors" +  
                            " as select pa.* from collab_paper_authors pa \
                            where pa.paper_id in (select id from sub_db.paper)"
                            )

        create_author_table = ("create table sub_db.author" +  
                            " as select a.id, a.affiliation_id, ins.university, a.country_id from collab_author a \
                              left join collab_institute ins \
                              on a.affiliation_id = ins.id  \
                            where a.id in (select distinct pa.author_id from sub_db.paper_authors pa)"
                            )       

        cur.execute(check_paper)
        if cur.fetchone()[0] == 1:
            msg = "sub database paper already exists"
        else:
            cur.execute(create_paper_table)
            cur.execute(check_paper_author)
            if cur.fetchone()[0] == 1:
                msg = "sub database paper_author already exists"
            else:
                cur.execute(create_paper_authors_table)
                cur.execute(check_author)
                if cur.fetchone()[0] == 1:
                    msg = "sub database author already exists" 
                else:
                    cur.execute(create_author_table)
                    msg = "create sub database successfully!"

        # query to return result ==> may be unnecessary
        query1 = ("select * from sub_db.paper")
        query2 = ("select * from sub_db.author")
        query3 = ("select * from sub_db.paper_authors")
        cur.execute(query1)
        name_1 = [i[0] for i in cur.description]
        res1 = cur.fetchall()
        cur.execute(query2)
        name_2 = [i[0] for i in cur.description]
        res2 = cur.fetchall()
        cur.execute(query3)
        name_3 = [i[0] for i in cur.description]
        res3 = cur.fetchall()
    return  json.dumps({"paper": [name_1,res1], "author": [name_2,res2], "paper_authors": [name_3,res3]})

def create_co_authors(topics, from_date, to_date):
    with sqlite3.connect(db_path + "/subDB_" + "".join(topics) + "_" + from_date + "_" + to_date + ".sqlite3") as conn:
        cur = conn.cursor()
        create_co_authors_table = ("create table co_author \
                                    as select pa1.paper_id, pa1.author_id as id_author_1, pa2.author_id as id_author_2 \
                                    from paper_authors pa1 \
                                    join paper_authors pa2 \
                                    on pa1.paper_id = pa2.paper_id and pa1.author_id < pa2.author_id order by pa1.paper_id"
                                )       
        check = "select count(name) from sqlite_master where type='table' and name='co_author'"
        cur.execute(check)
        if cur.fetchone()[0] == 1:
            msg = "co author table already exists"
            message ={ "msg" : msg, "name": "co_author"}
        else:
            cur.execute(create_co_authors_table)
            message = {"msg": "create co author table successfully!",
                    "name": "co author " + "_" + "_".join(topics)
            }

    # query to return result ==> may be unnecessary
    query = ("select distinct id_author_1, id_author_2 from co_author")
    cur.execute(query)
    column_names = [i[0] for i in cur.description]
    result = cur.fetchall()
    return json.dumps({"co_author": [column_names,result], "msg": message})

def create_potential_co_authors(topics, co_author_name, potential_co_author_name, from_date, to_date):   # could be used for time sliced potential
    temp = co_author_name
    message = []
    level = 1
    with sqlite3.connect(db_path + "/subDB_" + "".join(topics) + "_" + from_date + "_" + to_date + ".sqlite3") as conn:
        cur = conn.cursor()
        for i in range(level):
            if i > 0:
                temp = potential_co_author_name + str(i)
            create_potential_co_authors_table = ("create table " + potential_co_author_name + str(i+1) +
                                                " as \
                                                select co1.id_author_2 as id_author_1, co2.id_author_2 as id_author_2 \
                                                from " + temp + " co1 \
                                                join " + temp + " co2 \
                                                on co1.id_author_1 = co2.id_author_1 \
                                                and co1.id_author_2 < co2.id_author_2 \
                                                union \
                                                select co2.id_author_1 as id_author_1, co1.id_author_2 as id_author_2 \
                                                from " + temp + " co1 \
                                                join " + temp + " co2 \
                                                on co1.id_author_1 = co2.id_author_2 \
                                                and co1.id_author_2 > co2.id_author_1 \
                                                union \
                                                select co1.id_author_1 as id_author_1, co2.id_author_1 as id_author_2 \
                                                from " + temp + " co1 \
                                                join " + temp + " co2 \
                                                on co1.id_author_2 = co2.id_author_2 \
                                                and co1.id_author_1 < co2.id_author_1 \
                                                union \
                                                select co.id_author_1, co.id_author_2 \
                                                from " + temp + " co")
            name = potential_co_author_name + str(i+1) 
            check = "select count(name) from sqlite_master where type='table' and name='" + name + "'"
            cur.execute(check)
            if cur.fetchone()[0] == 1:
                msg = name + " already exists"
                message.append({"msg": msg})
            else:
                cur.execute(create_potential_co_authors_table)
                msg = "create " + potential_co_author_name + " table successfully"   
                message.append({"msg" : msg})

    # query to return result ==> may be unnecessary
    query = ("select * from " + potential_co_author_name + str(level))
    cur.execute(query)
    column_names = [i[0] for i in cur.description]
    result = cur.fetchall()
    return json.dumps({"last_potential": [column_names,result], "msg": message})


# def get_all_authors(topic, from_date,to_date):
#     _ = create_sub_tables([topic], from_date, to_date)
#     with sqlite3.connect(db_path + "/subDB_" + topic + "_" + from_date + "_" + to_date +'.sqlite3') as conn:
#         cur = conn.cursor()
#         cur.execute("ATTACH DATABASE '" + db_path + "/db.sqlite3' AS db")
#         query = ("select a.id, a.first_name, a.last_name from db.collab_author a\
#                   where a.id in (select id from author)  \
#                 ")
#         cur.execute(query)
#         result = cur.fetchall()
#         result = np.array(result)
#         id = result[:, 0]
#         first_name = result[:, 1]
#         last_name = result[:, 2]
#         return json.dumps({"id": list(id), "first_name": list(first_name), "last_name": list(last_name)}) 
 
def get_all_authors(data_name):
    data_name = os.path.basename(data_name)
    if data_name.endswith('.csv'):
        data_name = data_name[:-4]
    arr = data_name.split('_')
    
    # Handle both formats:
    # Format 1 (Coauthor_Candidate_Tables): Data_22_2000_2003_20021231 or Data_22_23_2000_2003_20021231
    # Format 2 (Clustering_Results): sSFCM_Data_22_2000_2003_20021231 or sSMCFCM_Data_22_2000_2003_20021231
    
    try:
        # Always: last 3 parts are [from_date, to_date, time_slice]
        # Parts in between: [prefix?], Data, [topics...], from_date, to_date, time_slice
        
        if len(arr) < 5:
            raise ValueError(f"Invalid filename format: {data_name}. Expected at least 4 underscores.")
        
        # Parse from the end
        time_slice = arr[-1]
        to_date = arr[-2]
        from_date = arr[-3]
        
        # Find the starting index based on prefix
        start_idx = 0
        if arr[0] in ['sSFCM', 'sSMCFCM', 'sSMC']:
            # Format like: sSFCM_Data_22_2000_2003_20021231
            if arr[1] != 'Data':
                raise ValueError(f"Invalid clustering filename format: {data_name}")
            start_idx = 2
        else:
            # Format like: Data_22_2000_2003_20021231
            if arr[0] != 'Data':
                raise ValueError(f"Invalid candidate filename format: {data_name}")
            start_idx = 1
        
        # Topics are between 'Data' (or prefix) and from_date
        topic_end_idx = len(arr) - 3
        topics = arr[start_idx:topic_end_idx]
        
        if not topics:
            raise ValueError(f"No topics found in filename: {data_name}")
        
        topic = topics[0]  # Use first topic for database file
        
    except (IndexError, ValueError) as e:
        print(f"Error parsing filename '{data_name}': {e}")
        # Return empty authors list as fallback
        return json.dumps({
            "id": [],
            "first_name": [],
            "last_name": [],
        })
    
    print(f"Parsed - Topics: {topics}, From: {from_date}, To: {to_date}, DB Topic: {topic}")
    
    with sqlite3.connect(db_path + "/subDB_" + topic + "_" + from_date + "_" + to_date +'.sqlite3') as conn:
        cur = conn.cursor()
        try:
            cur.execute("ATTACH DATABASE '" + db_path + "/db.sqlite3' AS db")
            query = ("select a.id, a.first_name, a.last_name from db.collab_author a\
                      where a.id in (select id from author)  \
                    ")
            print("Connect success!")
            cur.execute(query)
            result = cur.fetchall()
            
            if not result:
                # If no results, get authors from author table
                cur.execute("select id from author")
                ids = [row[0] for row in cur.fetchall()]
                return json.dumps({
                    "id": ids,
                    "first_name": ["Author" for _ in ids],
                    "last_name": [str(i) for i in ids],
                })
            
            result = np.array(result)
            if result.ndim < 2 or result.shape[1] < 3:
                # Fallback if result has unexpected shape
                ids = [row[0] for row in result] if result.ndim > 0 else []
                return json.dumps({
                    "id": ids,
                    "first_name": ["Author" for _ in ids],
                    "last_name": [str(i) for i in ids],
                })
            
            id = list(result[:, 0])
            first_name = [str(x) if x is not None else "N/A" for x in result[:, 1]]
            last_name = [str(x) if x is not None else "N/A" for x in result[:, 2]]
            
            # Ensure all arrays have the same length
            min_len = min(len(id), len(first_name), len(last_name))
            id = id[:min_len]
            first_name = first_name[:min_len]
            last_name = last_name[:min_len]
            
            return json.dumps({"id": id, "first_name": first_name, "last_name": last_name})
        except sqlite3.DatabaseError as e:
            print(f"DatabaseError: {e}")
            try:
                cur.execute("select id from author")
                ids = [row[0] for row in cur.fetchall()]
                return json.dumps({
                    "id": ids,
                    "first_name": ["Author" for _ in ids],
                    "last_name": [str(i) for i in ids],
                })
            except:
                return json.dumps({
                    "id": [],
                    "first_name": [],
                    "last_name": [],
                })
        except Exception as e:
            print(f"Error in get_all_authors: {e}")
            try:
                cur.execute("select id from author")
                ids = [row[0] for row in cur.fetchall()]
                return json.dumps({
                    "id": ids,
                    "first_name": ["Author" for _ in ids],
                    "last_name": [str(i) for i in ids],
                })
            except:
                return json.dumps({
                    "id": [],
                    "first_name": [],
                    "last_name": [],
                })