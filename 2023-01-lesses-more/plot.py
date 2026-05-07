besti = [1201, 1431, 1705, 4063, 4841, 5768, 13745, 16377, 19513, 46499, 55403, 66012, 157305]
for i in range(len(besti)-1):
    print(besti[i+1]/besti[i])
    
import matplotlib.pyplot as plt
plt.plot(besti)
plt.yscale('log')
plt.show()


    
    