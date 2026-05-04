"""Code for sSFCM algorithm"""
import pandas as pd
import numpy as np


class sSFCM():
    
    def __init__(self, *args, **kwargs):
        self.c = 2
        self.X = np.zeros(1)
        self.seed = None
        return
        
    def read_data(self, path):
        self.data = pd.read_csv(path)
        self.data = np.array(self.data)
        print(self.data)
    
    def preprocess_data(self, X, y):
        self.n = X.shape[0] #n là số mẫu dữ liệu
        self.p = X.shape[1]
        self.label = y
        self.label_list = pd.unique(y)
        self.label_list = self.label_list.tolist()
        self.num_class = len(self.label_list)
        self.X = np.array(X)
        
    
    def generate_U_ngang(self):
        # self.n = self.X.shape[0]
        self.U_ngang = np.zeros((self.n,self.c))
        self.index_supervised_sample = np.where(self.label==1)[0]
        print(self.index_supervised_sample)
        print(f"Số lượng phần tử đặt giám sát: {len(self.index_supervised_sample)}")
        for i in range(len(self.index_supervised_sample)):
            #c1 = self.dict_cluster[label[index_supervised_sample[i]]]
            self.U_ngang[self.index_supervised_sample[i]][0] = 0.5 #0 là cụm có nhãn ban đầu = +1
        # print(self.U_ngang.T)
        self.sum_i = sum(self.U_ngang.T)
        return self.sum_i

    def generate_V(self, data, k, seed):
        data = pd.DataFrame(data)
        self.V = data.sample(k, random_state=seed).values
        print(self.V)

    def generate_U(self):
        self.U = np.zeros((self.n,self.c))

    # Tinh d_ki (trong cong thuc 6)
    def d_ki(self,k, i):
        kq = sum(pow(self.X[k] - self.V[i], 2))
        return kq     
        
    #Cong thuc so 6
    def cong_thuc_6(self, m): #Don't clear
        # print(self.c)
        Z = np.zeros((self.n,self.c))
        #tu day suy ra U = U_ngang + Z ta tinh Z

        D = np.zeros((self.n,self.c))
        for k in range(self.n):
            for i in range(self.c):
                D[k][i] = pow(self.d_ki(k,i),1/(1-m))
                D[k][i] = np.nan_to_num(D[k][i])
            D[k] = D[k]/sum(D[k])
            D[k] = np.nan_to_num(D[k])
      
        #Z = (1/d_ki)^1/m-1z = np.array (i = 1 ,c)
        for i in range(self.n) :
            Z[i] = (1 - self.sum_i[i] )*D[i]
        print((self.U_ngang+Z).shape)
        self.U = self.U_ngang+Z  # tuc la U  
        return self.U
    
    def cong_thuc_4(self,m): #Tính tâm của cụm
        V_temp = np.zeros((self.c,self.p))
        U_temp = abs(self.U - self.U_ngang)
        U_temp = pow(U_temp,m)
        for i in range(self.c):
            tu_so = np.zeros(self.p)
            for k in range(self.n):
                tu_so +=U_temp[k][i] * self.X[k] 
            V_temp[i] = tu_so/ sum((U_temp.T)[i])
        return V_temp
    
    
    def train_sSFCM(self,eps,m,l):
        loop = 1
        Epsilon = np.zeros((self.c,self.p)) + eps
        self.generate_U_ngang()
        self.generate_V(self.X,self.c,seed=1)
        while True:
            print("Lần lặp: ",loop)
            self.U= self.cong_thuc_6(m)
            V_truoc = self.V
            self.V= self.cong_thuc_4(m)
            delta_V = abs(self.V- V_truoc)
            check = np.less_equal(delta_V, Epsilon)
            
            if (np.all(check) or loop ==l):
                break
            loop += 1
        ans = self.count_class()
        print(f"Số mẫu dương ban đầu: {ans}")
        return self.U, self.V
    
    def count_class(self):
        self.count_class_cluster = np.zeros((self.num_class,self.c), dtype="int64")
        for k in range(self.n):
            k_class = self.label_list.index(self.label[k])
            index_max = np.argmax(self.U[k])
            self.count_class_cluster[k_class][index_max] +=1 
        return self.count_class_cluster[1][0]
    
    # def clusering_sSFCM(self,eps,m,l):
    #     while True:
    #         print("m1 = ",m1)
    #         self.U, self.V = self.train_sSFCM(eps,m,l)
    #         self.num_supervisor = self.count_class()
    #         print(f"Number of supervisors: {self.num_supervisor}")
    #         if self.num_supervisor == len(self.index_supervised_sample):
    #             break
    #         else:
    #             m1 += 1 
    #     return self.U, self.V
    

    def assign_label(self):
        self.new_label = np.zeros(self.n)
        for k in range(self.n):
            index_max = np.argmax(self.U[k])
            if(index_max == 0):
                self.new_label[k] = 1
            else:
                self.new_label[k] = -1
        return self.new_label  

    
    def freeMemory(self):
        self.U = None
        self.U_ngang = None
        self.c = None
        self.V = None