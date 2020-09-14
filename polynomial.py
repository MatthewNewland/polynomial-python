from __future__ import annotations
from typing import List


class Polynomial:

    coeffs: List[int]
    disp_ch: str = 'x'

    def __init__(self, coeffs, *, disp_ch=None):
        self.coeffs = coeffs
        if disp_ch:
            self.disp_ch = disp_ch
    
    def __str__(self) -> str:
        """
        Return a string representing the polynomial. Use self.disp_ch ('x' by default) as the base.
        Since `coeffs` stores coefficients in order of ascending powers, this method returns a string
        representing the polynomial in ascending power order. So:
        >>> p = Polynomial([7, 14, 23])
        >>> str(p)
        '7 + 14x + 23x^2'
        >>> q = Polynomial([14, 12, 9, 11], disp_ch='z')
        >>> str(q)
        '14 + 12z + 9z^2 + 11z^3'
        """
        retlist = []

        for (pow, coeff) in enumerate(self.coeffs):
            if coeff == 0:
                continue
            if coeff == 1:
                coeff_part = ""
            else:
                coeff_part = str(coeff)
            if pow == 0:
                pow_part = ""
            elif pow == 1:
                pow_part = self.disp_ch
            else:
                pow_part = f"{self.disp_ch}^{pow}"

            retlist.append(f'{coeff_part}{pow_part}')
 
        ret = " + ".join(retlist).replace("+ -", "- ")
        return ret
    
    def __repr__(self) -> str:
        return f'{type(self).__name__}({str(self)})'

    def __add__(self, other: Polynomial) -> Polynomial:
        """
        Return the result of polynomial addition with `other`.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> q = Polynomial([9, 12, 3])
        >>> p + q
        Polynomial(12 + 16x + 8x^2 + 9x^3)
        """
        new_coeffs = [0] * max(len(self.coeffs), len(other.coeffs))
        
        for (pow, coeff) in enumerate(self.coeffs):
            new_coeffs[pow] += coeff
        
        for (pow, coeff) in enumerate(other.coeffs):
            new_coeffs[pow] += coeff

        return Polynomial(new_coeffs)

    def __sub__(self, other: Polynomial) -> Polynomial:
        """
        Return the result of polynomial subtraction of `other` from this polynomial.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> q = Polynomial([9, 12, 3])
        >>> p - q
        Polynomial(-6 - 8x + 2x^2 + 9x^3)
        """
        new_coeffs = [0] * max(len(self.coeffs), len(other.coeffs))
        
        for (pow, coeff) in enumerate(self.coeffs):
            new_coeffs[pow] += coeff
        
        for (pow, coeff) in enumerate(other.coeffs):
            new_coeffs[pow] -= coeff

        return Polynomial(new_coeffs)

    def __mul__(self, other: Polynomial) -> Polynomial:
        """
        Return the result of polynomial multiplication with `other`.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> q = Polynomial([9, 12, 3])
        >>> p * q
        Polynomial(27 + 72x + 102x^2 + 153x^3 + 123x^4 + 27x^5)
        """
        new_coeffs = [0] * (len(self.coeffs) + len(other.coeffs) - 1)
        
        for (i, i_co) in enumerate(self.coeffs):
            for (j, j_co) in enumerate(other.coeffs):
                new_coeffs[i + j] += i_co * j_co
        
        return Polynomial(new_coeffs)

    def derivative(self) -> Polynomial:
        """
        Return the derivative of this polynomial.
        >>> p = Polynomial([3, 4, 5, 9])
        >>> p.derivative()
        Polynomial(4 + 10x + 27x^2)
        """
        if len(self.coeffs) in (0, 1):
            return Polynomial([0])
        else:
            new_coeffs = []
            for (pow, coeff) in enumerate(self.coeffs):
                new_coeffs.append(pow * coeff)
            return Polynomial(new_coeffs[1:])

if __name__ == '__main__':
    import doctest
    doctest.testmod()
