import urllib, sys
import json
import requests
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from sklearn.linear_model import LinearRegression


#Paralar
paraUSD = 100.0
paraETH = 0.0
paraSafe = 0.0
zaman = 0

def paraYatir(x,y):
    global ys
    if ys[-1][0] > 0 and y > 0 :
        if x:
            return y/ys[-1][0]#X = True USD -> ETH
        elif not x:
            return ys[-1][0]*y#X = False ETH -> USD
    else :
        return 0.0




#Zaman
def arrayEkle(a,b):
    return np.concatenate((a, b), axis=0)


#Figure preparasyonu
fig = plt.figure()
fig.canvas.set_window_title('LR 5')
style.use('fivethirtyeight')
ax1 = fig.add_subplot(1,1,1)

#Regresyon preparasyonu
print("X / Y")
aa = str(input("x ->>")).upper()
ab = str(input("y ->>")).upper()
f = open("Log_LR5_"+aa+"_vs_"+ab+"_"+str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))+".csv",'w')
f.write("YS,XS,Total Money,Time\n")

def setasas():


    global fsyms_list, aa, ab
    fsyms_list = [aa]

    global fsym
    fsym = ','.join(fsyms_list)

    global tsyms_list
    tsyms_list = [ab]

    global tsym
    tsym = ','.join(tsyms_list)

    global api_address
    api_address = 'https://min-api.cryptocompare.com/data/pricemulti?'

    now = datetime.now()

    global url
    url = api_address + urllib.parse.urlencode({'fsyms':fsym,'tsyms':tsym})

    response = requests.get(url).json()

    global xs
    xs = np.array([[int(float(str(now.hour)+'.'.join([str(now.minute),str(now.second)]))*100)]])

    global ys
    ys = np.array([[response[aa][ab]]])


setasas()

def XYGuncelle():
    global xs, ys,aa,ab, xpred
    now = datetime.now()
    response = requests.get(url).json()
    xs = arrayEkle(xs,np.array([[int(float(str(now.hour)+'.'.join([str(now.minute),str(now.second)]))*100)]]))
    ys = arrayEkle(ys,np.array([[response[aa][ab]]]))
    xpred = arrayEkle(xs,[[xs[-1][0]+5],[xs[-1][0]+10]])


def animate(i):
    global paraUSD, paraETH, paraSafe ,xs, ys, aa, ab, xpred, zaman
    regressor = LinearRegression()
    while datetime.now().second % 5 == 0 :
        XYGuncelle()
        if xs.size > 6 and ys.size > 6:
            xs = np.delete(xs,0,0)
            ys = np.delete(ys,0,0)
        if xpred.size > 8 :
            xpred = np.delete(xpred,0,0)
        ax1.clear()
        print("\n  XS\n"+str(xs)+"\n\n  YS\n"+str(ys)+"\n\n  XPRED\n"+str(xpred))
        if xs.size > 5 and ys.size > 5:
            regressor.fit(xs[-5:],ys[-5:]) #Son uc icin -4 yap
            ypred = regressor.predict(xpred[-3:])
            print("\nYPRED\n"+str(ypred))
            ax1.plot(xpred[-3:],ypred,color='r',zorder=1)
            if ypred[-1][0] > ypred[0][0]:
                paraETH += paraYatir(True,paraUSD)
                paraUSD = 0.0
                print("\n1) Converted to "+aa+"\n"+ab+" ->"+str(paraUSD)+"\t"+aa+" ->"+str(paraETH))
            elif ypred[0][0] > ypred[-1][0]:
                paraUSD += paraYatir(False,paraETH)
                paraETH = 0.0
                print("\n2) Converted to "+ab+"\n"+ab+" ->"+str(paraUSD)+"\t"+aa+" ->"+str(paraETH))
            else :
                paraUSD += paraYatir(False,paraETH)
                paraETH = 0.0
                print("\n3) Stable\n"+ab+"\n"+ab+" ->"+str(paraUSD)+"\t"+aa+" ->"+str(paraETH))

            if paraUSD+paraETH*ys[-1][0] > 100:
                paraSafe += paraUSD+paraETH*ys[-1][0]-100
                paraUSD -= paraUSD+paraETH*ys[-1][0]-100
            print("TOTAL MONEY 5 ->> "+str(paraUSD+paraETH*ys[-1][0]+paraSafe))
            f.write(str(ys[0,0])+',')
            f.write(str(xs[0,0])+',')
            f.write(str(paraUSD+paraETH*ys[-1][0])+',')
            zaman += 1
            f.write(str(zaman)+'\n')


        ax1.plot(xs,ys,color="g",zorder=2)
        ax1.scatter(xs,ys,color="b",zorder=3)
try:
    ani = animation.FuncAnimation(fig, animate, interval=900)
    plt.show()
except Exception as e:
        f.close()
        sys.exit()
