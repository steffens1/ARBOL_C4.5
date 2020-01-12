import math
class C45:

    def __init__(self, archivo_datos,archivo_descripcion):
        self.archivo_datos = archivo_datos
        self.archivo_descripcion = archivo_descripcion
        self.data = []
        self.clases = []
        self.numero_atributos = -1 
        self.valores_de_atributos = {}
        self.atributos = []
        self.arbol = None

    def Obtener_datos(self):
        with open(self.archivo_descripcion, "r") as file:
            clases = file.readline()
            self.clases = [x.strip() for x in clases.split(",")]
            for line in file:
                [atributo, valores] = [x.strip() for x in line.split(":")]
                valores = [x.strip() for x in valores.split(",")]
                self.valores_de_atributos[atributo] = valores
        self.numero_atributos = len(self.valores_de_atributos.keys())
        self.atributos = list(self.valores_de_atributos.keys())
        with open(self.archivo_datos, "r") as file:
            for line in file:
                fila = [x.strip() for x in line.split(",")]
                if fila != [] or fila != [""]:
                    self.data.append(fila)

    def prepocesar_datos(self):
        for indice,fila in enumerate(self.data):
            for attr_indice in range(self.numero_atributos):
                if(not self.es_atributo_discreto(self.atributos[attr_indice])):
                    self.data[indice][attr_indice] = float(self.data[indice][attr_indice])

    def printarbol(self):
        self.mostrar_nodo(self.arbol)

    def mostrar_nodo(self, nodo, identacion=""):
        if not nodo.esHoja:
            if nodo.limite is None:
                for indice,hijo in enumerate(nodo.hijoren):
                    if hijo.esHoja:
                        print(identacion + nodo.etiqueta + " = " + nodo.valores_de_atributo[nodo.etiqueta][indice] + " : " + hijo.etiqueta)
                    else:
                        print(identacion + nodo.etiqueta + " = " + nodo.valores_de_atributo[nodo.etiqueta][indice] + " : ")
                        self.mostrar_nodo(hijo, identacion + "    ")
            else:
                hijo_izquierdo = nodo.hijoren[0]
                hijo_derecho = nodo.hijoren[1]
                if hijo_izquierdo.esHoja:
                    print(identacion + nodo.etiqueta + " <= " + str(nodo.limite) + " : " + hijo_izquierdo.etiqueta)
                else:
                    print(identacion + nodo.etiqueta + " <= " + str(nodo.limite)+" : ")
                    self.mostrar_nodo(hijo_izquierdo, identacion + "    ")

                if hijo_derecho.esHoja:
                    print(identacion + nodo.etiqueta + " > " + str(nodo.limite) + " : " + hijo_derecho.etiqueta)
                else:
                    print(identacion + nodo.etiqueta + " > " + str(nodo.limite) + " : ")
                    self.mostrar_nodo(hijo_derecho , identacion + "    ")



    def generar_arbol(self):
        self.arbol = self.generar_arbol_recursivamente(self.data, self.atributos)

    def generar_arbol_recursivamente(self, curData, curatributos):
        
        misma_clases = self.misma_clase(curData)

        if len(curData) == 0:
            #Fail
            return Nodo(True, "Fail", None , None )
        elif misma_clases is not False:
            return Nodo(True, misma_clases, None , None )
        elif len(curatributos) == 0:
            majClass = self.getMajClass(curData)
            return Nodo(True, majClass, None)
        else:
            (mejor,mejor_limite,separado_) = self.separar_atributos(curData, curatributos)
            atributos_restantes = curatributos[:]
            atributos_restantes.remove(mejor)
            nodo = Nodo(False, mejor, mejor_limite , self.valores_de_atributos)
            nodo.hijoren = [self.generar_arbol_recursivamente(subset, atributos_restantes) for subset in separado_]
            return nodo

    def getMajClass(self, curData):
        freq = [0]*len(self.clases)
        for fila in curData:
            indice = self.clases.index(fila[-1])
            freq[indice] += 1
        maxInd = freq.index(max(freq))
        return self.clases[maxInd]


    def misma_clase(self, data):
        for fila in data:
            if fila[-1] != data[0][-1]:
                return False
        return data[0][-1]

    def es_atributo_discreto(self, atributo):
        if atributo not in self.atributos:
            raise ValueError("atributo not listed")
        elif len(self.valores_de_atributos[atributo]) == 1 and self.valores_de_atributos[atributo][0] == "continuous":
            return False
        else:
            return True

    def separar_atributos(self, curData, curatributos):
        separado_ = []
        maxEnt = -1*float("inf")
        mejor_atributo = -1
        #None for discrete atributos, limite value for continuous atributos
        mejor_limite = None
        for atributo in curatributos:
            indice_de_atributo = self.atributos.index(atributo)
            if self.es_atributo_discreto(atributo):
                #split curData into n-sub_conjuntos, where n is the number of 
                #different valores of atributo i. Choose the atributo with
                #the max ganancia
                valores_para_atributoo = self.valores_de_atributos[atributo]
                sub_conjuntos = [[] for a in valores_para_atributoo]
                for fila in curData:
                    for indice in range(len(valores_para_atributoo)):
                        if fila[indice_de_atributo] == valores_para_atributoo[indice]:
                            sub_conjuntos[indice].append(fila)
                e = self.ganancia(curData, sub_conjuntos)
                if e > maxEnt:
                    maxEnt = e
                    separado_ = sub_conjuntos
                    mejor_atributo = atributo
                    mejor_limite = None
            else:
                #sort the data according to the column.Then try all 
                #possible adjacent pairs. Choose the one that 
                #yields maximum ganancia
                curData.sort(key = lambda x: x[indice_de_atributo])
                for j in range(0, len(curData) - 1):
                    if curData[j][indice_de_atributo] != curData[j+1][indice_de_atributo]:
                        limite = (curData[j][indice_de_atributo] + curData[j+1][indice_de_atributo]) / 2
                        less = []
                        greater = []
                        for fila in curData:
                            if(fila[indice_de_atributo] > limite):
                                greater.append(fila)
                            else:
                                less.append(fila)
                        e = self.ganancia(curData, [less, greater])
                        if e >= maxEnt:
                            separado_ = [less, greater]
                            maxEnt = e
                            mejor_atributo = atributo
                            mejor_limite = limite
        return (mejor_atributo,mejor_limite,separado_)

    def ganancia(self,unionSet, sub_conjuntos):

        S = len(unionSet)
        impureza_antes_de_separar = self.entropia(unionSet)
        pesos = [len(subset)/S for subset in sub_conjuntos]
        impureza_depues_de_separar = 0
        for i in range(len(sub_conjuntos)):
            impureza_depues_de_separar += pesos[i]*self.entropia(sub_conjuntos[i])
        totalGain = impureza_antes_de_separar - impureza_depues_de_separar
        return totalGain

    def entropia(self, dataSet):
        S = len(dataSet)
        if S == 0:
            return 0
        num_clases = [0 for i in self.clases]
        for fila in dataSet:
            classindice = list(self.clases).index(fila[-1])
            num_clases[classindice] += 1
        num_clases = [x/S for x in num_clases]
        ent = 0
        for num in num_clases:
            ent += num*self.log(num)
        return ent*-1


    def log(self, x):
        if x == 0:
            return 0
        else:
            return math.log(x,2)

class Nodo:
    def __init__(self,esHoja, etiqueta, limite , valores_de_atributo ):
        self.etiqueta = etiqueta
        self.limite = limite
        self.esHoja = esHoja
        self.hijoren = []
        self.valores_de_atributo = valores_de_atributo
