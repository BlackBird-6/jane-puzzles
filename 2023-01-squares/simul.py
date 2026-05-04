import matplotlib

def f(n1, n2, n3, n4, res):
    print(n1,n2,n3,n4,res)
    if n1 == 0 and n2 == 0 and n3 == 0 and n4 == 0:
        return res
    return f(abs(n1 - n2), abs(n2 - n3), abs(n3 - n4), abs(n4 - n1), res + 1)

print(f(187427,85525,30122,0,1))