import numpy
import sympy

from ..helpers import Eval135


class EvalCartesian(Eval135):
    """Evaluate spherical harmonics degree by degree `n` at angles `polar`, `azimuthal`.
    """

    def __init__(self, X, scaling, complex_valued=True, symbolic="auto"):
        assert len(X) == 3
        # assert X[0] ** 2 + X[1] ** 2 + X[2] ** 2 == 1

        if symbolic == "auto":
            symbolic = numpy.asarray(X).dtype == sympy.Basic

        # Conventions from
        # <https://en.wikipedia.org/wiki/Spherical_harmonics#Orthogonality_and_normalization>.
        rc = {
            "acoustic": RCSpherical(False, symbolic, geodetic=False),
            "quantum mechanic": RCSpherical(True, symbolic, geodetic=False),
            "geodetic": RCSpherical(False, symbolic, geodetic=True),
            "schmidt": RCSchmidt(False, symbolic),
        }[scaling]

        if complex_valued:
            #
            # x = sin(polar) * cos(azimuthal)
            # y = sin(polar) * sin(azimuthal)
            # z = cos(polar)
            #
            # exp_iphi
            # = exp(imag_unit * azimuthal)
            # = (X[0] + imag_unit * X[1]) / sqrt(X[0] ** 2 + X[1] ** 2)
            #
            # sqrt(1 - X[2]**2) / exp(i * phi)
            # = (X[0] ** 2 + X[1] ** 2) / (X[0] + imag_unit * X[1])
            # = X[0] - imag_unit * X[1]
            #
            # sqrt(1 - X[2]**2) * exp(i * phi)
            # = X[0] + imag_unit * X[1]
            #
            imag_unit = sympy.I if symbolic else 1j
            xi = [
                X[0] - imag_unit * X[1],
                X[0] + imag_unit * X[1],
            ]
        else:
            # real-valued, but not always a polynomial; see associated Legendre
            # functions
            sqrt = sympy.sqrt if symbolic else numpy.sqrt
            a = sqrt(X[0] ** 2 + X[1] ** 2)
            xi = [a, a]

        super().__init__(rc, X[2], xi, symbolic=symbolic)


class EvalSpherical(Eval135):
    """Evaluate spherical harmonics degree by degree `n` at angles `polar`, `azimuthal`.
    """

    def __init__(self, theta_phi, scaling, complex_valued=True, symbolic="auto"):
        assert len(theta_phi) == 2
        if symbolic == "auto":
            symbolic = numpy.asarray(theta_phi).dtype == sympy.Basic

        # Conventions from
        # <https://en.wikipedia.org/wiki/Spherical_harmonics#Orthogonality_and_normalization>.
        rc = {
            "acoustic": RCSpherical(False, symbolic, geodetic=False),
            "quantum mechanic": RCSpherical(True, symbolic, geodetic=False),
            "geodetic": RCSpherical(False, symbolic, geodetic=True),
            "schmidt": RCSchmidt(False, symbolic),
        }[scaling]

        sin = numpy.vectorize(sympy.sin) if symbolic else numpy.sin
        cos = numpy.vectorize(sympy.cos) if symbolic else numpy.cos

        # X = [
        #     sin_polar * cos_azimu,
        #     sin_polar * sin_azimu,
        #     cos_polar,
        # ]

        if complex_valued:
            sin_theta, sin_phi = sin(theta_phi)
            cos_theta, cos_phi = cos(theta_phi)

            imag_unit = sympy.I if symbolic else 1j
            exp_i_phi = cos_phi + imag_unit * sin_phi
            xi = [sin_theta / exp_i_phi, sin_theta * exp_i_phi]
        else:
            theta = theta_phi[0]
            sin_theta = sin(theta)
            cos_theta = cos(theta)
            xi = [sin_theta, sin_theta]

        super().__init__(rc, cos_theta, xi, symbolic=symbolic)


class RCSpherical:
    def __init__(self, with_cs_phase, symbolic, geodetic):
        pi = sympy.pi if symbolic else numpy.pi
        self.sqrt = numpy.vectorize(sympy.sqrt) if symbolic else numpy.sqrt
        self.S = sympy.S if symbolic else lambda x: x

        # The starting value 1 has the effect of multiplying the entire tree by
        # sqrt(4*pi). This convention is used in geodesy and and spectral
        # analysis.
        self.p0 = 1 if geodetic else 1 / self.sqrt(4 * pi)
        self.phase = -1 if with_cs_phase else 1

    def __getitem__(self, L):
        L = self.S(L)

        z0 = self.sqrt((2 * L + 1) / (2 * L))
        z1 = z0 * self.phase
        #
        m = numpy.arange(-L + 1, L)
        c0 = self.sqrt((2 * L - 1) * (2 * L + 1) / ((L + m) * (L - m)))
        #
        if L == 1:
            c1 = None
        else:
            m = numpy.arange(-L + 2, L - 1)
            c1 = self.sqrt(
                (L + m - 1)
                * (L - m - 1)
                * (2 * L + 1)
                / ((2 * L - 3) * (L + m) * (L - m))
            )
        return z0, z1, c0, c1


class RCSchmidt:
    def __init__(self, with_cs_phase, symbolic):
        self.sqrt = numpy.vectorize(sympy.sqrt) if symbolic else numpy.sqrt
        self.S = sympy.S if symbolic else lambda x: x
        self.phase = -1 if with_cs_phase else 1

        # if phi is None:
        #     self.p0 = 2
        self.p0 = 1

    def __getitem__(self, L):
        L = self.S(L)

        z0 = self.sqrt((2 * L - 1) / (2 * L))
        z1 = z0 * self.phase
        #
        m = numpy.arange(-L + 1, L)
        c0 = (2 * L - 1) / self.sqrt((L + m) * (L - m))
        #
        if L == 1:
            c1 = None
        else:
            m = numpy.arange(-L + 2, L - 1)
            c1 = self.sqrt((L + m - 1) * (L - m - 1) / ((L + m) * (L - m)))

        return z0, z1, c0, c1