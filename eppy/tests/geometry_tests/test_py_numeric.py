# Copyright (c) 2014 Eric Youngson

# This file is part of eppy.

# Eppy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Eppy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with eppy.  If not, see <http://www.gnu.org/licenses/>.

"""pytest for py_numeric.py"""
# Written by Eric Youngson eric@successionecological.com / eayoungs@gmail.com
# Succession Ecological Services: Portland, Oregon

import eppy.geometry.py_numeric as py_numeric
from eppy.pytest_helpers import almostequal


# Start vector cross product tests
def test_vctr_cross():
    """test the cross product of two 3 dimentional vectors"""

    # Vector cross-product.
    x = [1, 2, 3]
    y = [4, 5, 6]
    z = py_numeric.vctr_cross(x, y)

    assert z == [-3, 6, -3]


def test_2dim_cross():
    """test the cross product of two 2 dimentional vectors"""

    # 2 dim cross-product.
    x = [1, 2]
    y = [4, 5]
    z = py_numeric.vctr_cross(x, y)

    assert z == 'ERROR'


def test_4dim_cross():
    """test the cross product of two 2 dimentional vectors"""

    # 4 dim cross-product.
    x = [1, 2, 3, 4]
    y = [5, 6, 7, 8]
    z = py_numeric.vctr_cross(x, y)

    assert z == 'ERROR'


def test_mdim_cross():
    """test the cross product of two 4 dimentional vectors"""

    # Mixed dim cross-product.
    x = [1, 2, 3]
    y = [4, 5, 6, 7]
    z = py_numeric.vctr_cross(x, y)

    assert z == 'ERROR'


# Start vector dot product tests
def test_vctr_dot():
    """test the dot product of two mixed dimentional vectors"""

    # Vector dot-product.
    x = [1, 2, 3]
    y = [4, 5, 6]
    z = py_numeric.vctr_dot(x, y)

    assert z == [4, 10, 18]


def test_2dim_dot():
    """test the dot product of two 2 dimentional vectors"""

    # 2 dim dot-product.
    x = [1, 2]
    y = [4, 5]
    z = py_numeric.vctr_dot(x, y)

    assert z == 'ERROR'


def test_4dim_dot():
    """test the dot product of two 4 dimentional vectors"""

    # 4 dim dot-product.
    x = [1, 2, 3, 4]
    y = [5, 6, 7, 8]
    z = py_numeric.vctr_dot(x, y)

    assert z == 'ERROR'


def test_mdim_dot():
    """test the dot product of two mixed dimentional vectors"""

    # Mixed dim dot-product.
    x = [1, 2, 3]
    y = [4, 5, 6, 7]
    z = py_numeric.vctr_dot(x, y)

    assert z == 'ERROR'
