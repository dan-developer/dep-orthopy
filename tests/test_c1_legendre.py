import itertools

import numpy as np
import pytest
import scipy.special
import sympy
from helpers import get_nth
from sympy import S, sqrt

import orthopy


@pytest.mark.parametrize(
    "scaling, n, y",
    [
        ("monic", 0, [1, 1, 1]),
        ("monic", 1, [0, S(1) / 2, 1]),
        ("monic", 2, [-S(1) / 3, -S(1) / 12, S(2) / 3]),
        ("monic", 3, [0, -S(7) / 40, S(2) / 5]),
        ("monic", 4, [S(3) / 35, -S(37) / 560, S(8) / 35]),
        ("monic", 5, [0, S(23) / 2016, S(8) / 63]),
        #
        ("classical", 0, [1, 1, 1]),
        ("classical", 1, [0, S(1) / 2, 1]),
        ("classical", 2, [-S(1) / 2, -S(1) / 8, 1]),
        ("classical", 3, [0, -S(7) / 16, 1]),
        ("classical", 4, [S(3) / 8, -S(37) / 128, 1]),
        ("classical", 5, [0, S(23) / 256, 1]),
        #
        ("normal", 0, [sqrt(S(1) / 2), sqrt(S(1) / 2), sqrt(S(1) / 2)]),
        ("normal", 1, [0, sqrt(S(3) / 8), sqrt(S(3) / 2)]),
        ("normal", 2, [-sqrt(S(5) / 8), -sqrt(S(5) / 128), sqrt(S(5) / 2)]),
        ("normal", 3, [0, -sqrt(S(343) / 512), sqrt(S(7) / 2)]),
        ("normal", 4, [9 / sqrt(2) / 8, -111 / sqrt(2) / 128, 3 / sqrt(2)]),
        ("normal", 5, [0, sqrt(S(5819) / 131072), sqrt(S(11) / 2)]),
    ],
)
def test_legendre_monic(scaling, n, y):
    x = np.array([0, S(1) / 2, 1])

    # Test evaluation of one value
    y0 = get_nth(orthopy.c1.legendre.Eval(x[0], scaling, symbolic=True), n)
    assert y0 == y[0]

    # Test evaluation of multiple values
    val = get_nth(orthopy.c1.legendre.Eval(x, scaling, symbolic=True), n)
    assert all(val == y)


def _integrate(f, x):
    return sympy.integrate(f, (x, -1, +1))


def test_integral0(n=4):
    x = sympy.Symbol("x")
    evaluator = orthopy.c1.legendre.Eval(x, "normal", symbolic=True)

    assert _integrate(next(evaluator), x) == sqrt(2)
    for _ in range(n + 1):
        assert _integrate(next(evaluator), x) == 0


def test_normality(n=4):
    x = sympy.Symbol("x")
    evaluator = orthopy.c1.legendre.Eval(x, "normal", symbolic=True)
    for _ in range(n + 1):
        assert _integrate(next(evaluator) ** 2, x) == 1


def test_orthogonality(n=4):
    x = sympy.Symbol("x")
    evaluator = orthopy.c1.legendre.Eval(x, "normal", symbolic=True)
    vals = [next(evaluator) for _ in range(n + 1)]
    for f0, f1 in itertools.combinations(vals, 2):
        assert _integrate(f0 * f1, x) == 0


@pytest.mark.parametrize(
    "t, ref",
    [
        (sympy.S(1) / 2, sympy.S(23) / 2016),
        (1, sympy.S(8) / 63),
        (np.array([1]), np.array([sympy.S(8) / 63])),
        (np.array([1, 2]), np.array([sympy.S(8) / 63, sympy.S(1486) / 63])),
    ],
)
def test_eval(t, ref, tol=1.0e-14):
    n = 5
    value = get_nth(orthopy.c1.legendre.Eval(t, "monic", symbolic=True), n)
    assert np.all(value == ref)

    # Evaluating the Legendre polynomial in this way is rather unstable, so don't go too
    # far with n.
    approx_ref = np.polyval(scipy.special.legendre(n, monic=True), t)
    assert np.all(np.abs(value - approx_ref) < tol)


def test_show(n=5):
    orthopy.c1.legendre.show(n, "normal")
    orthopy.c1.legendre.savefig("legendre.svg", n, "normal")


if __name__ == "__main__":
    test_show()
    # plt.savefig("line-segment-legendre.png", transparent=True)
