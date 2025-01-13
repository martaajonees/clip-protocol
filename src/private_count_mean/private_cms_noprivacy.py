from sympy import primerange
import random
import numpy as np
import importlib.util
import os
import argparse
import time
from progress.bar import Bar
from tabulate import tabulate
import sys

# Enlace con la ruta para las utilidades (funciones de uso comun)
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  'utils', 'utils.py'))
module_name = 'utils'

spec = importlib.util.spec_from_file_location(module_name, file_path)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

TEST_MODE = False

class privateCMS:
    def __init__(self, k, m, dataset, domain):
        self.k = k 
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.N = len(dataset)
        
        # Creación de la matriz de sketch
        self.M = np.zeros((self.k, self.m))

        # Definimos la familia de hashes independientes 3 a 3
        primos = list(primerange(10**6, 10**7))
        p = primos[random.randint(0, len(primos)-1)]
        self.H = utils.generate_hash_functions(self.k,p, 3,self.m)

    def client(self, d):
        j = random.randint(0, self.k-1)
        v = np.full(self.m, -1)
        selected_hash = self.H[j]
        v[selected_hash(d)] = 1
        return v, j
   
    def actualizar_matriz_sketch(self,d):
        for i in range (self.k):
            selected_hash = self.H[i]
            hash_index = selected_hash(d)
            self.M[i ,hash_index] += 1

    def estimar_d(self,d):
        min_estimation = float('inf')
        for i in range(self.k):
            selected_hash = self.H[i]
            min_estimation = min(min_estimation, self.M[i,selected_hash(d)])
        return min_estimation
    
    def execute(self):
        bar = Bar('Procesando datos de los clientes', max=len(self.dataset), suffix='%(percent)d%%')

        for d in self.dataset:
            self.actualizar_matriz_sketch(d)
            bar.next()
        bar.finish()

        F_estimada = {}
        bar = Bar('Obteniendo histograma de frecuencias estimadas', max=len(self.domain), suffix='%(percent)d%%')
        for x in self.domain:
            F_estimada[x] = self.estimar_d(x)
            bar.next()
        bar.finish()
        return F_estimada


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Algoritmo Private Count Mean Sketch para la estimación de frecuencias a partir de un dominio conocido.")
    parser.add_argument("-k", type=int, required=True, help="Numero de funciones hash empleadas (Nº Filas en la matriz de sketch).")
    parser.add_argument("-m", type=int, required=True, help="Valor máximo del dominio de las funciones hash (Nº de columnas de la matriz de sketch)")
    parser.add_argument("-d", type=str, required=True, help='Nombre del dataset empleado')
    parser.add_argument("--verbose_time", action="store_true", help="Se desea obtener los tiempos de ejecución de las funciones.")
    args = parser.parse_args()

    dataset,df, domain = utils.load_dataset(args.d)

    PCMS = privateCMS(args.k,args.m,dataset,domain)
    f_estimada = PCMS.execute()

    os.system('cls' if os.name == 'nt' else 'clear>/dev/null')

    utils.display_results(df,f_estimada)


  
