import math

import numpy as np
import pytest
import sympy

import orthopy


def test_stieltjes():
    n = 5
    alpha0, beta0, int_1 = orthopy.tools.stieltjes(
        lambda t, ft: sympy.integrate(ft, (t, -1, 1)), n
    )

    rc = orthopy.c1.legendre.RecurrenceCoefficients("monic", symbolic=True)
    _, alpha1, beta1 = np.array([rc[k] for k in range(n)]).T

    assert (alpha0 == alpha1).all()
    assert (beta0 == beta1).all()
    assert int_1 == rc.int_1


def test_golub_welsch(tol=1.0e-14):
    """Test the custom Gauss generator with the weight function x ** 2."""
    alpha = 2.0

    # Get the moment corresponding to the weight function omega(x) =
    # x^alpha:
    #
    #                                     / 0 if k is odd,
    #    int_{-1}^{+1} |x^alpha| x^k dx ={
    #                                     \ 2 / (alpha + k + 1) if k is even.
    #
    n = 5
    moments = [0 if k % 2 == 1 else 2 / (k + alpha + 1) for k in range(2 * n + 1)]
    alpha, beta, int_1 = orthopy.tools.golub_welsch(moments)

    assert np.all(abs(alpha) < tol)
    assert math.isnan(beta[0])
    assert abs(beta[1] - 3.0 / 5.0) < tol
    assert abs(beta[2] - 4.0 / 35.0) < tol
    assert abs(beta[3] - 25.0 / 63.0) < tol
    assert abs(beta[4] - 16.0 / 99.0) < tol
    assert abs(int_1 - math.sqrt(2.0 / 3.0)) < tol

    orthopy.tools.gautschi_test_3(moments, alpha, beta)


@pytest.mark.parametrize("dtype", [float, sympy.S])
def test_chebyshev(dtype):
    alpha = 2

    # Get the moments corresponding to the weight function omega(x) =
    # x^alpha:
    #
    #                                     / 0 if k is odd,
    #    int_{-1}^{+1} |x^alpha| x^k dx ={
    #                                     \ 2/(alpha+k+1) if k is even.
    #
    n = 5

    if dtype == sympy.S:
        moments = [sympy.S(1 + (-1) ** kk) / (kk + alpha + 1) for kk in range(2 * n)]

        alpha, beta, int_1 = orthopy.tools.chebyshev(moments)

        assert all([a == 0 for a in alpha])
        assert math.isnan(beta[0])
        assert (
            beta[1:]
            == [sympy.S(3) / 5, sympy.S(4) / 35, sympy.S(25) / 63, sympy.S(16) / 99]
        ).all()
        assert int_1 == sympy.S(2) / 3
    else:
        assert dtype == float
        tol = 1.0e-14
        k = np.arange(2 * n)
        moments = (1.0 + (-1.0) ** k) / (k + alpha + 1)

        alpha, beta, int_1 = orthopy.tools.chebyshev(moments)

        assert np.all(abs(alpha) < tol)
        assert np.isnan(beta[0])
        assert np.all(abs(beta[1:] - [3 / 5, 4 / 35, 25 / 63, 16 / 99]) < tol)
        assert abs(int_1 - 2 / 3) < tol


def test_chebyshev_modified(tol=1.0e-14):
    alpha = 2.0

    # Get the moments corresponding to the Legendre polynomials and the weight
    # function omega(x) = |x^alpha|:
    #
    #                                        / 2/3   if k == 0,
    #    int_{-1}^{+1} |x^alpha| P_k(x) dx ={  8/45  if k == 2,
    #                                        \ 0     otherwise.
    #
    n = 5
    moments = np.zeros(2 * n)
    moments[0] = 2.0 / 3.0
    moments[2] = 8.0 / 45.0

    rc = orthopy.c1.legendre.RecurrenceCoefficients("monic", symbolic=False)
    alpha, beta, int_1 = orthopy.tools.chebyshev_modified(moments, rc)

    assert np.all(abs(alpha) < tol)
    assert math.isnan(beta[0])
    assert np.all(abs(beta[1:] - [3 / 5, 4 / 35, 25 / 63, 16 / 99]) < tol)
    assert abs(int_1 - 2 / 3) < tol
