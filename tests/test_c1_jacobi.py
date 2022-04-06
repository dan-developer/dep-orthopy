import math

import numpy as np
import pytest
from helpers import get_nth
from sympy import S, sqrt

import orthopy


@pytest.mark.parametrize(
    "scaling, n, y",
    [
        ("monic", 0, [1, 1, 1]),
        ("monic", 1, [S(1) / 7, S(9) / 14, S(8) / 7]),
        ("monic", 2, [-S(1) / 9, S(1) / 4, S(10) / 9]),
        ("monic", 3, [-S(1) / 33, S(7) / 264, S(32) / 33]),
        ("monic", 4, [S(3) / 143, -S(81) / 2288, S(112) / 143]),
        ("monic", 5, [S(1) / 143, -S(111) / 4576, S(256) / 429]),
        #
        ("classical", 0, [1, 1, 1]),
        ("classical", 1, [S(1) / 2, S(9) / 4, 4]),
        ("classical", 2, [-1, S(9) / 4, 10]),
        ("classical", 3, [-S(5) / 8, S(35) / 64, 20]),
        ("classical", 4, [S(15) / 16, -S(405) / 256, 35]),
        ("classical", 5, [S(21) / 32, -S(2331) / 1024, 56]),
        #
        ("normal", 0, [sqrt(15) / 4, sqrt(15) / 4, sqrt(15) / 4]),
        ("normal", 1, [sqrt(10) / 8, 9 * sqrt(10) / 16, sqrt(10)]),
        ("normal", 2, [-sqrt(35) / 8, 9 * sqrt(35) / 32, 5 * sqrt(35) / 4]),
        ("normal", 3, [-sqrt(210) / 32, 7 * sqrt(210) / 256, sqrt(210)]),
        ("normal", 4, [3 * sqrt(210) / 64, -81 * sqrt(210) / 1024, 7 * sqrt(210) / 4]),
        ("normal", 5, [3 * sqrt(105) / 64, -333 * sqrt(105) / 2048, 4 * sqrt(105)]),
    ],
)
def test_jacobi_monic(scaling, n, y):
    x = np.array([0, S(1) / 2, 1])

    alpha = 3
    beta = 2

    evaluator = orthopy.c1.jacobi.Eval(x[2], scaling, alpha, beta, symbolic=True)

    y2 = get_nth(evaluator, n)
    assert y2 == y[2]

    evaluator = orthopy.c1.jacobi.Eval(x, scaling, alpha, beta, symbolic=True)
    val = get_nth(evaluator, n)
    assert all(val == y)


@pytest.mark.parametrize("symbolic", [True, False])
def test_jacobi(symbolic):
    n = 5
    rc = orthopy.c1.jacobi.RecurrenceCoefficients("monic", 1, 1, symbolic)
    alpha, beta, gamma = np.array([rc[k] for k in range(n)]).T

    if symbolic:
        assert np.all(alpha == 1)
        assert np.all(beta == 0)
        assert np.all(gamma == [None, S(1) / 5, S(8) / 35, S(5) / 21, S(8) / 33])
    else:
        tol = 1.0e-14
        assert np.all(np.abs(alpha - 1) < tol)
        assert np.all(np.abs(beta) < tol)
        ref_gamma = [math.nan, 1 / 5, 8 / 35, 5 / 21, 8 / 33]
        assert math.isnan(gamma[0])
        assert np.all(np.abs(gamma[1:] - ref_gamma[1:]) < tol)


def test_show(n=5):
    orthopy.c1.jacobi.show(n, "normal", 0, 0)
    orthopy.c1.jacobi.savefig("jacobi.svg", n, "normal", 0, 0)


if __name__ == "__main__":
    test_show()
