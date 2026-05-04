"""Code for sSMC-FCM algorithm"""
from typing_extensions import final
import pandas as pd
import numpy as np
import math
from random import random
import random

class sSMC_FCM():
    
    def __init__(self, *args, **kwargs):
        self.X = np.zeros(1)
        self.seed = None
        self.c = 2
        return
   
    def read_data(self, path):
        self.data = pd.read_csv(path , header = None)
        self.data_table = np.array(self.data)

    def preprocess_data(self, X, y):
        self.n = X.shape[0] 
        self.p = X.shape[1]
        self.label = y
        self.label_list = pd.unique(y)
        self.label_list = self.label_list.tolist()
        self.num_class = len(self.label_list)
        self.X = np.array(X)


    def generate_M(self,m,m1):
        self.M = np.zeros((self.n,self.c))
        self.index_x_giamsat = np.where(self.label==1)[0]
        # print(len(self.index_x_giamsat))
        # print(self.index_x_giamsat)
        for i in range(self.n):
            if i in self.index_x_giamsat:
                self.M[i] = m
                self.M[i][0] = m1 #đặt vị trí giám sát vào cụm đầu tiên (cụm có nhãn 1)
            else:
                self.M[i] = m
        # print(self.M.tolist())

    def generate_V(self, seed):
        self.X = pd.DataFrame(self.X)
        self.V = self.X.sample(self.c, random_state=seed).values   
        self.V_truoc=self.V   
        return   

    def generate_U(self):
        self.U=np.zeros((self.n,self.c))
        return
    
    def update_D(self):
        self.X = np.array(self.X)
        self.D=np.zeros((self.n,self.c))
        for i in range(self.n):
            for k in range(self.c):
                self.D[i][k]=math.sqrt(sum(pow(self.X[i]-self.V[k],2)))
        return
    
    def solve_mu(self,sum_mu_i,d_ik,m,m1,epsilon):# Tính nuy_ik (công thức 19) sử dụng pp lặp nhị phân
        epsilon = epsilon/1000
        mu = 0
        vp = pow(1/(m1*d_ik*d_ik),1/(m1-1))
        vt = -1
        left = 0.0
        right = 1.0
        while (abs(vt-vp) > epsilon):
            mu = (right + left)/2
            vt = mu/pow(mu + sum_mu_i, (m1-m)/(m1-1))  
            if vt<vp:
                left = mu
            else:
                right =mu
            if abs(mu - (right + left)/2) <=epsilon:
                break
        return mu

    def update_U(self,m,m1,epsilon):
        self.update_D()
        for i in range(self.n):
            if i not in self.index_x_giamsat:
                for k in range(self.c):
                    # print(f"D[{i}]: ",self.D[i])
                    # print(f"D[{i}][{k}]: ",self.D[i][k])
                    mau_so = sum(pow(self.D[i][k] / self.D[i], 2/(m-1)))
                    #mau_so = np.nan_to_num(mau_so)
                    self.U[i][k] = np.nan_to_num(1/mau_so)
            elif i in self.index_x_giamsat:
                d_min = np.amin(self.D[i])
                d_i = self.D[i]/d_min
                mu_i = np.zeros(self.c)
                for j in range(self.c):
                    if (self.M[i][j]==m):
                        mu_i[j]=1/pow( m *d_i[j]*d_i[j] , 1/(m-1) )
                sum_mu_i=sum(mu_i)
                for j in range(self.c):
                    if (self.M[i][j]==m1):
                        mu_i[j] = self.solve_mu(sum_mu_i, d_i[j], m, m1 , epsilon)
                        
                self.U[i] = mu_i/sum(mu_i)
        return self.U

    def update_V(self):
        V_temp=np.zeros((self.c,self.p))
        for k in range(self.c):
            temp=pow((self.U.T)[k],(self.M.T)[k])
            tu_so=np.zeros(self.p)
            for i in range(self.n):
                tu_so+=temp[i]*self.X[i]
            V_temp[k]=tu_so/sum(temp)
        return V_temp

    def count_class(self):
        self.count_class_cluster = np.zeros((self.num_class,self.c), dtype="int64")
        for k in range(self.n):
            k_class = self.label_list.index(self.label[k])
            index_max = np.argmax(self.U[k])
            self.count_class_cluster[k_class][index_max] +=1 
        return self.count_class_cluster[1][0]
    
    def train_sSMC_FCM(self,m,m1,eps,l):
        self.generate_V(seed=1)
        self.generate_U()
        epsilon = np.zeros((self.c,self.p)) + eps
        self.generate_M(m,m1)
        loop = 0
        while True:
            print("Lần lặp: ",loop)
            print("m1 = ",m1)
            self.update_U(m,m1,eps)
            self.V_truoc=self.V
            self.V=self.update_V()
            delta_V=abs(self.V-self.V_truoc)
            check = np.less_equal(delta_V, epsilon)
            if (np.all(check) or loop ==l):
                break
            loop +=1
        return self.U, self.V
                
    def clusering_sSMC_FCM(self,m,m1,eps,l):
        while True:
            print("m1 = ",m1)
            self.U, self.V = self.train_sSMC_FCM(m, m1, eps, l)
            self.num_supervisor = self.count_class()
            print(f"Number of supervisors: {self.num_supervisor}")
            if self.num_supervisor == len(self.index_x_giamsat):
                break
            else:
                m1 += 1 
        return self.U, self.V
                
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
        self.M = None
        self.c = None
        self.index_x_giamsat = None
        self.V = None
        self.D = None
        self.V_truoc = None
        return


