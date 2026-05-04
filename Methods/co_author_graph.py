from collections import defaultdict
import sqlite3

#db_path = 'D:/Dongtacgia/Project3/Project3/Data_Project3/subDB_22_23_2015_2016.sqlite3'
class Edge:
    def __init__(self, w):
        self.w = w
        # self.days = []
        # self.months = []
        self.years = defaultdict(int)     # store number of papers written in year
        self.max_time_pattern = 0  # store the latest time that 2 author cowork
    def add_time(self, year, month, day):
        # self.days.append(day)
        # self.months.append(month)
        self.years[year] += 1

class Vertice:
    def __init__(self, id, university, country_id):
        self.id = id
        self.university = university
        self.country_id = country_id
    

class Co_Author_Graph:
    def __init__(self, db_path):
        self.list_vertices = defaultdict(Vertice)
        self.adj = defaultdict(dict)
        self.time_patterns = set() # used to store all years of publication; could be month or smth else
        print(db_path)
        # create list of vertices:
        with sqlite3.connect(db_path) as conn:
            print("----------Start creating co author graph: Vertice----------")
            cur = conn.cursor() 
            cur.execute("select a.id, a.university, a.country_id from author a")
            res = cur.fetchall()
            for row in res:
                if row[1] == None and row[2] == None:
                    self.list_vertices[row[0]] = Vertice(row[0], "None", -1)
                if row[1] == None and row[2] != None:
                    self.list_vertices[row[0]] = Vertice(row[0], "None", row[2])
                if row[2] == None and row[1] != None:
                    self.list_vertices[row[0]] = Vertice(row[0], row[1], -1)
                if row[2] != None and row[1] != None:
                    self.list_vertices[row[0]] = Vertice(row[0], row[1], row[2])
            print("----------Finish creating co author graph: Vertice----------")
        #crete adj
        with sqlite3.connect(db_path) as conn:
            print("----------Start creating co author graph----------")
            cur = conn.cursor()
            get_co_author = ("select co.id_author_1, co.id_author_2, p.date from co_author co \
                        join paper p \
                        on co.paper_id = p.id" \
                        )
            cur.execute(get_co_author)
            records = cur.fetchall()   
            for row in records:
                u = row[0]
                v = row[1]
                date = row[2].split("-")
                year, month, day = int(date[0]), int(date[1]), int(date[2])
                self.time_patterns.add(year)
                if v in self.adj[u].keys():
                    self.adj[u][v].w += 1
                    self.adj[u][v].add_time(year, month, day)
                    self.adj[u][v].max_time_pattern = max(self.adj[u][v].max_time_pattern, year)
                    self.adj[v][u].w += 1
                    self.adj[v][u].add_time(year, month, day)
                    self.adj[v][u].max_time_pattern = max(self.adj[v][u].max_time_pattern, year)
                else:
                    self.adj[u][v] = Edge(1)
                    self.adj[u][v].add_time(year, month, day)
                    self.adj[u][v].max_time_pattern = max(self.adj[u][v].max_time_pattern, year)
                    self.adj[v][u] = Edge(1)
                    self.adj[v][u].add_time(year, month, day)
                    self.adj[v][u].max_time_pattern = max(self.adj[v][u].max_time_pattern, year)
            self.time_patterns = sorted(self.time_patterns, reverse=True)
            print("----------Finish creating co author graph----------")