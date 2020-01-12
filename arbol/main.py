import pdb
from c45 import C45

c1 = C45("../data/clima/clima_datos.data", "../data/clima/clima_names.names")

c1.Obtener_datos()
c1.prepocesar_datos()
c1.generar_arbol()
c1.printarbol()