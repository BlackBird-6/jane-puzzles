# FIND THE TWENTIETH SMALLEST NUMBER WITH DIGITS TOTALING TWENTY-SIX
# =3599
seen = 0
for i in range(10**8):
    if(sum([int(k) for k in str(i)]) == 26):
        seen += 1
        print(f"Number {seen}: {i}")
        if seen == 20:
            break
