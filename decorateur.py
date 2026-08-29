def carres_liste(n):
    resultat = []
    for i in range(n):
        resultat.append(i * i)
    return resultat

def carres_generateur(n):
    for i in range(n):
        yield i * i

gen = carres_generateur(10000000)
print(next(gen))
print(next(gen))
print(next(gen))
print(next(gen))
print(next(gen))
print('list :', carres_liste(10000000))