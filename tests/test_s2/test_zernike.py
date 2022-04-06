import itertools

import numpy as np
import pytest
import sympy
from helpers_s2 import _integrate_poly

import orthopy

X = sympy.symbols("x, y")
P = [sympy.poly(x, X) for x in X]


def test_zernike_vals():
    from math import factorial as fact

    # explicit formula for R_n^m
    def r(n, m, rho):
        assert n >= m >= 0
        assert (n - m) % 2 == 0
        s = 0.0
        for k in range((n - m) // 2 + 1):
            s += (
                (-1) ** k
                * fact(n - k)
                / fact(k)
                / fact((n + m) // 2 - k)
                / fact((n - m) // 2 - k)
                * rho ** (n - 2 * k)
            )
        return s

    np.random.seed(0)
    rho, phi = np.random.rand(2)

    xy = [rho * np.cos(phi), rho * np.sin(phi)]
    iterator = orthopy.s2.zernike.Eval(xy, "classical")
    for n, vals in enumerate(itertools.islice(iterator, 5)):
        for m, val in zip(range(-n, n + 1, 2), vals):
            fun = np.sin if m < 0 else np.cos
            ref = r(n, abs(m), rho) * fun(abs(m) * phi)
            assert abs(ref - val) < 1.0e-12 * abs(ref)


def test_zernike_explicit():
    x, y = X
    ref = [
        [1],
        [y, x],
        [2 * x * y, 2 * (x ** 2 + y ** 2) - 1, x ** 2 - y ** 2],
        [
            3 * x ** 2 * y - y ** 3,
            3 * (x ** 2 + y ** 2) * y - 2 * y,
            3 * (x ** 2 + y ** 2) * x - 2 * x,
            x ** 3 - 3 * y ** 2 * x,
        ],
        [
            4 * y * x ** 3 - 4 * y ** 3 * x,
            (4 * (x ** 2 + y ** 2) - 3) * 2 * x * y,
            6 * (x ** 2 + y ** 2) ** 2 - 6 * (x ** 2 + y ** 2) + 1,
            (4 * (x ** 2 + y ** 2) - 3) * (x ** 2 - y ** 2),
            x ** 4 - 6 * x ** 2 * y ** 2 + y ** 4,
        ],
        [
            5 * y * x ** 4 - 10 * y ** 3 * x ** 2 + y ** 5,
            (5 * (x ** 2 + y ** 2) - 4) * (3 * y * x ** 2 - y ** 3),
            (10 * (x ** 2 + y ** 2) ** 2 - 12 * (x ** 2 + y ** 2) + 3) * y,
            (10 * (x ** 2 + y ** 2) ** 2 - 12 * (x ** 2 + y ** 2) + 3) * x,
            (5 * (x ** 2 + y ** 2) - 4) * (x ** 3 - 3 * y ** 2 * x),
            x ** 5 - 10 * y ** 2 * x ** 3 + 5 * y ** 4 * x,
        ],
    ]
    iterator = orthopy.s2.zernike.Eval(X, "classical")
    for ref_level, vals in zip(ref, itertools.islice(iterator, 6)):
        for r, val in zip(ref_level, vals):
            # r = sympy.simplify(r)
            # val = sympy.simplify(val)
            assert sympy.simplify(r - val) == 0, f"ref = {r}  !=   {val}"


@pytest.mark.parametrize(
    "scaling,int0", [("classical", sympy.pi), ("normal", sympy.sqrt(sympy.pi))]
)
def test_zernike_integral0(scaling, int0, n=4):
    iterator = orthopy.s2.zernike.Eval(P, scaling)
    for k, vals in enumerate(itertools.islice(iterator, n)):
        if k == 0:
            assert _integrate_poly(vals[0]) == int0
        else:
            for val in vals:
                assert _integrate_poly(val) == 0


@pytest.mark.parametrize("scaling", ["classical", "normal"])
def test_zernike_orthogonality(scaling, n=4):
    evaluator = orthopy.s2.zernike.Eval(P, scaling)
    vals = np.concatenate([next(evaluator) for _ in range(n + 1)])
    for f0, f1 in itertools.combinations(vals, 2):
        assert _integrate_poly(f0 * f1) == 0


def test_zernike_normality(n=5):
    iterator = orthopy.s2.zernike.Eval(P, "normal")
    for vals in itertools.islice(iterator, n):
        for val in vals:
            assert _integrate_poly(val ** 2) == 1


@pytest.mark.parametrize("degrees", [(2, 1)])
def test_show(degrees, scaling="normal"):
    orthopy.s2.zernike.show_single(degrees)


@pytest.mark.parametrize("n", [2])
def test_show_tree(n, scaling="normal"):
    orthopy.s2.zernike.show_tree(n, scaling=scaling, colorbar=True, clim=(-1.7, 1.7))
    orthopy.s2.zernike.savefig_tree(
        "disk-zernike-tree.png", n, scaling=scaling, colorbar=True, clim=(-1.7, 1.7)
    )


if __name__ == "__main__":
    # test_show((3, 2), "normal")
    test_show_tree(5, "normal")
