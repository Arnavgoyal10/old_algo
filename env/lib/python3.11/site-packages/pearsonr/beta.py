import math


def contfractbeta(a: float, b: float, x: float, itmax: int = 200) -> float:
    # https://malishoaib.wordpress.com/2014/04/15/the-beautiful-beta-functions-in-raw-python/
    # evaluates the continued fraction form of the incomplete Beta function; incompbeta()
    # code translated from: Numerical Recipes in C

    eps = 3.0e-7
    bm = az = am = 1.0
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    bz = 1.0 - qab * x / qap

    for i in range(itmax + 1):
        em = float(i + 1)
        tem = em + em
        d = em * (b - em) * x / ((qam + tem) * (a + tem))
        ap = az + d * am
        bp = bz + d * bm
        d = -(a + em) * (qab + em) * x / ((qap + tem) * (a + tem))
        app = ap + d * az
        bpp = bp + d * bz
        aold = az
        am = ap / bpp
        bm = bp / bpp
        az = app / bpp
        bz = 1.0
        if abs(az - aold) < (eps * abs(az)):
            return az

    message = 'a or b too large or given itmax too small for computing incomplete beta function.'
    raise ValueError(message)


def incompbeta(a: float, b: float, x: float) -> float:
    # https://malishoaib.wordpress.com/2014/04/15/the-beautiful-beta-functions-in-raw-python/
    # evaluates incomplete beta function, here a, b > 0 and 0 <= x <= 1
    # this function requires contfractbeta(a,b,x, itmax = 200)
    # code translated from: Numerical Recipes in C
    if x == 0 or x == 1:
        return x
    else:
        lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
        if x < (a + 1) / (a + b + 2):
            return math.exp(lbeta) * contfractbeta(a, b, x) / a
        else:
            return 1 - math.exp(lbeta) * contfractbeta(b, a, 1 - x) / b
