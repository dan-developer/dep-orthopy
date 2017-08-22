# -*- coding: utf-8 -*-
#
import math
import numpy
import orthopy
from scipy.special import legendre


def test_coefficients_from_moments(tol=1.0e-14):
    '''Test the custom Gauss generator with the weight function x**2.
    '''
    alpha = 2.0

    # Get the moment corresponding to the weight function omega(x) =
    # x^alpha:
    #
    #                                     / 0 if k is odd,
    #    int_{-1}^{+1} |x^alpha| x^k dx ={
    #                                     \ 2/(alpha+k+1) if k is even.
    #
    n = 5
    k = numpy.arange(2*n+1)
    moments = (1.0 + (-1.0)**k) / (k + alpha + 1)
    alpha, beta = orthopy.coefficients_from_moments(n, moments)

    assert numpy.all(abs(alpha) < tol)
    assert abs(beta[0] - 2.0/3.0) < tol
    assert abs(beta[1] - 3.0/5.0) < tol
    assert abs(beta[2] - 4.0/35.0) < tol
    assert abs(beta[3] - 25.0/63.0) < tol
    assert abs(beta[4] - 16.0/99.0) < tol

    orthopy.check_coefficients(moments, alpha, beta)
    return


def test_jacobi(tol=1.0e-14):
    n = 5
    a = 1.0
    b = 1.0
    alpha, beta = orthopy.jacobi_recursion_coefficients(n, a, b)

    assert numpy.all(abs(alpha) < tol)
    assert abs(beta[0] - 4.0/3.0) < tol
    assert abs(beta[1] - 1.0/5.0) < tol
    assert abs(beta[2] - 8.0/35.0) < tol
    assert abs(beta[3] - 5.0/21.0) < tol
    assert abs(beta[4] - 8.0/33.0) < tol
    return


def test_gauss(tol=1.0e-14):
    n = 5

    # weight function 1.0
    k = numpy.arange(2*n+1)
    moments = (1.0 + (-1.0)**k) / (k + 1)

    scheme = orthopy.Gauss(n, moments)

    s = math.sqrt(5.0 + 2*math.sqrt(10.0/7.0)) / 3.0
    t = math.sqrt(5.0 - 2*math.sqrt(10.0/7.0)) / 3.0
    assert abs(scheme.points[0] + s) < tol
    assert abs(scheme.points[1] + t) < tol
    assert abs(scheme.points[2] + 0.0) < tol
    assert abs(scheme.points[3] - t) < tol
    assert abs(scheme.points[4] - s) < tol

    u = 128.0/225.0
    v = (322.0 + 13 * math.sqrt(70)) / 900.0
    w = (322.0 - 13 * math.sqrt(70)) / 900.0
    assert abs(scheme.weights[0] - w) < tol
    assert abs(scheme.weights[1] - v) < tol
    assert abs(scheme.weights[2] - u) < tol
    assert abs(scheme.weights[3] - v) < tol
    assert abs(scheme.weights[4] - w) < tol
    return


def test_jacobi_reconstruction(tol=1.0e-14):
    alpha1, beta1 = orthopy.jacobi_recursion_coefficients(4, 2.0, 1.0)
    points, weights = orthopy.scheme_from_coefficients(alpha1, beta1)

    alpha2, beta2 = orthopy.coefficients_from_scheme(points, weights)

    assert numpy.all(abs(alpha1 - alpha2) < tol)
    assert numpy.all(abs(beta1 - beta2) < tol)
    return


def test_eval(tol=1.0e-14):
    n = 5
    alpha, beta = orthopy.jacobi_recursion_coefficients(n, 0.0, 0.0)
    t = 1.0
    value = orthopy.evaluate_orthogonal_polynomial(alpha, beta, t)

    ref = numpy.polyval(legendre(n, monic=True), t)

    assert abs(value - ref) < tol
    return


if __name__ == '__main__':
    test_eval()
