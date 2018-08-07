from collections import deque
import time
from datetime import datetime

print("\n1er exemple simple d'utilisation d'une deque pour gérer une queue circulaire\n")

circQueue = deque(maxlen=4)
s = ''

while True:
    if s.upper() == 'Q':
        break
    currTime = datetime.utcnow().strftime('%H:%M:%S')
    circQueue.append(currTime)
    print(circQueue) 
    s = input('any key to continue, q to jump to next example: ')

print("\n2ème exemple: la deque contient des entiers dont on calcule la moyenne mobile\n")

circQueue = deque(maxlen=4)
s = ''
i = 0

while True:
    if s.upper() == 'Q':
        break
    circQueue.append(i)
    i += 1
    print(circQueue, end=' ')
    print('sum:' , end=' ')
    print(sum(circQueue), end=' ')
    print('moving avg:' , end=' ')
    print(sum(circQueue) / 4)
    s = input('any key to continue, q to jump to next example: ')

print("\n3ème exemple plus proche des besoin de C2. Ici, on ajoute à la deque des paires")
print("de valeurs (volume et prix) que l'on place en couple dans une liste. On calcule")
print("la moyenne mobile du prix pondéré par le volume\n")

circQueue = deque(maxlen=4)
s = ''
volume = 1
price = 100

while True:
    if s.upper() == 'Q':
        break
    circQueue.append([volume, price])
    volume += 1
    price += 10
    
    print(circQueue, end=' ')
    
    movingVolume = sum(x[0] for x in circQueue)
    print('mVol:' , end=' ')
    print(movingVolume, end=' ')
    
    movingTotal = sum(x[0] * x[1] for x in circQueue)
    print('mPrVolTot:' , end=' ')
    print(movingTotal, end=' ')

    movingAvg = movingTotal / movingVolume
    print('mPrAvg:' , end=' ')
    print('{:3.2f}'.format(movingAvg))

    s = input('any key to continue, q to jump to next example: ')
