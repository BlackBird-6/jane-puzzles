import matplotlib

def f(n1, n2, n3, n4, res):
    # print(n1,n2,n3,n4,res)
    if n1 == 0 and n2 == 0 and n3 == 0 and n4 == 0:
        return res
    return f(abs(n1 - n2), abs(n2 - n3), abs(n3 - n4), abs(n4 - n1), res + 1)

# print(f(10,6,3,1,1))

N = 10_000_000
best = 0
bestarr = []

ratioX = 1.1914878255690124
ratioY = 2.382975822577713

ratioA = 2.1914878909476756
ratioB = 2.8392867657160803

i_candidates = [157305]

# ratioA = 2.1914878909476756
# ratioB = 2.8392867657160803
# +/- 0.000001

def find_next_i(last_i, r):
    global best
    for i in range(int(last_i*r - 0.001*last_i*r), int(last_i*r + 0.001*last_i*r)):
        j_lower = int(i/ratioA - 0.000001*i)
        j_upper = int(i/ratioA + 0.000001*i)+1

        for j in range(j_lower, j_upper):
            k_lower = int(j/ratioB - 0.000001*j)
            k_upper = int(j/ratioB + 0.000001*j)+1
            for k in range(k_lower,k_upper):
                l = 0
                if f(i,j,k,l,1) > best:
                    print(f"# NEW BEST: {f(i,j,k,l,1)}: {i} {j} {k} {l} sums to {i+j+k+l} with ratios {i/j if j>0 else 0} {j/k if k>0 else 0}")
                    best = f(i,j,k,l,1)
                    i_candidates.append(i)


while len(i_candidates) > 0:
    last_i = i_candidates.pop(0)
    find_next_i(last_i,ratioX)
    find_next_i(last_i,ratioY)
    


   

# NEW BEST: 5: 1 0 0 0 sums to 1
# NEW BEST: 7: 3 1 0 0 sums to 4
# NEW BEST: 8: 4 2 1 0 sums to 7
# NEW BEST: 9: 9 4 1 0 sums to 14
# NEW BEST: 10: 11 5 2 0 sums to 18
# NEW BEST: 11: 13 6 2 0 sums to 21
# NEW BEST: 12: 31 14 5 0 sums to 50
# NEW BEST: 13: 37 17 6 0 sums to 60
# NEW BEST: 14: 44 20 7 0 sums to 71
# NEW BEST: 15: 105 48 17 0 sums to 170
# NEW BEST: 16: 125 57 20 0 sums to 202
# NEW BEST: 17: 149 68 24 0 sums to 241
# NEW BEST: 18: 355 162 57 0 sums to 574
# NEW BEST: 19: 423 193 68 0 sums to 684
# NEW BEST: 20: 504 230 81 0 sums to 815

# Based on these results it looks like we can just set the last term
# to always be 0 for optimization (N^4 -> N^3)

# # NEW BEST: 8: 4 2 1 0 sums to 7 with ratios 2.0 2.0
# NEW BEST: 9: 9 4 1 0 sums to 14 with ratios 2.25 4.0
# NEW BEST: 10: 11 5 2 0 sums to 18 with ratios 2.2 2.5
# NEW BEST: 11: 13 6 2 0 sums to 21 with ratios 2.1666666666666665 3.0
# NEW BEST: 12: 31 14 5 0 sums to 50 with ratios 2.2142857142857144 2.8
# NEW BEST: 13: 37 17 6 0 sums to 60 with ratios 2.176470588235294 2.8333333333333335
# NEW BEST: 14: 44 20 7 0 sums to 71 with ratios 2.2 2.857142857142857
# NEW BEST: 15: 105 48 17 0 sums to 170 with ratios 2.1875 2.823529411764706
# NEW BEST: 16: 125 57 20 0 sums to 202 with ratios 2.192982456140351 2.85
# NEW BEST: 17: 149 68 24 0 sums to 241 with ratios 2.1911764705882355 2.8333333333333335
# NEW BEST: 18: 355 162 57 0 sums to 574 with ratios 2.191358024691358 2.8421052631578947
# NEW BEST: 19: 423 193 68 0 sums to 684 with ratios 2.1917098445595853 2.838235294117647
# NEW BEST: 20: 504 230 81 0 sums to 815 with ratios 2.1913043478260867 2.8395061728395063

# NEW BEST: 20: 504 230 81 0 sums to 815 with ratios 2.1913043478260867 2.8395061728395063
# NEW BEST: 21: 1201 548 193 0 sums to 1942 with ratios 2.1916058394160585 2.839378238341969
# NEW BEST: 22: 1431 653 230 0 sums to 2314 with ratios 2.1914241960183767 2.8391304347826085
# NEW BEST: 23: 1705 778 274 0 sums to 2757 with ratios 2.191516709511568 2.8394160583941606
# NEW BEST: 24: 4063 1854 653 0 sums to 6570 with ratios 2.191477885652643 2.8392036753445637
# NEW BEST: 25: 4841 2209 778 0 sums to 7828 with ratios 2.1914893617021276 2.839331619537275
# NEW BEST: 26: 5768 2632 927 0 sums to 9327 with ratios 2.1914893617021276 2.8392664509169365

# looks like it's approaching some ratio

# NEW BEST: 27: 13745 6272 2209 0 sums to 22226 with ratios 2.191485969387755 2.839293798098687
# NEW BEST: 28: 16377 7473 2632 0 sums to 26482 with ratios 2.1914893617021276 2.8392857142857144
# NEW BEST: 29: 19513 8904 3136 0 sums to 31553 with ratios 2.1914869721473496 2.8392857142857144
# NEW BEST: 30: 46499 21218 7473 0 sums to 75190 with ratios 2.1914883589405223 2.8392881038404925

# ratioA = 2.1914883589405223
# ratioB = 2.8392881038404925
# +/- 0.0001

# NEW BEST: 31: 55403 25281 8904 0 sums to 89588 with ratios 2.1914876784937305 2.8392857142857144
# NEW BEST: 32: 66012 30122 10609 0 sums to 106743 with ratios 2.19148794900737 2.839287397492695
# NEW BEST: 33: 157305 71780 25281 0 sums to 254366 with ratios 2.1914878796322097 2.8392864206320
# NEW BEST: 34: 187427 85525 30122 0 sums to 303074 with ratios 2.1914878690441393 2.839286899940243

# Best i values include
# [1201, 1431, 1705, 4063, 4841, 5768, 13745, 16377, 19513, 46499, 55403, 66012, 157305]

# Either of ratios
# ratioX = 1.1914878255690124
# ratioY = 2.382975822577713

# NEW BEST: 35: 223317 101902 35890 0 sums to 361109 with ratios 2.1914879001393497 2.839286709389802
# NEW BEST: 36: 532159 242830 85525 0 sums to 860514 with ratios 2.191487872173949 2.839286758257819
# NEW BEST: 37: 634061 289329 101902 0 sums to 1025292 with ratios 2.1914878909476756 2.8392867657160803

# ratioA = 2.1914878909476756
# ratioB = 2.8392867657160803
# +/- 0.000001

# NEW BEST: 38: 755476 344732 121415 0 sums to 1221623 with ratios 2.1914878804404583 2.8392867438125435
# NEW BEST: 39: 1800281 821488 289329 0 sums to 2911098 with ratios 2.191487885398204 2.839286763511435
# NEW BEST: 40: 2145013 978793 344732 0 sums to 3468538 with ratios 2.191487883546368 2.8392867502871795
# NEW BEST: 41: 2555757 1166220 410744 0 sums to 4132721 with ratios 2.1914878839327057 2.839286757688487
# NEW BEST: 42: 6090307 2779074 978793 0 sums to 9848174 with ratios 2.1914878840937666 2.8392867541962397
# NEW BEST: 43: 7256527 3311233 1166220 0 sums to 11733980 with ratios 2.191487883818505 2.8392867555006776
# NEW BEST: 44: 8646064 3945294 1389537 0 sums to 13980895 with ratios 2.191487884046157 2.8392867

# So M = 44 (max M obtained on S)

# Constraint is 0 <= a, b, c, d <= 10,000,000 so we are now done
# Answer is 8646064;3945294;1389537;0

# THE END

# 4:41~5:48