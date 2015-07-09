# EPlusInterface (EPI) - An interface for EnergyPlus
# Copyright (C) 2004 Santosh Philip

# This file is part of EPlusInterface.
#
# EPlusInterface is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# EPlusInterface is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EPlusInterface; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


# Santosh Philip, the author of EPlusInterface, can be contacted at the following email address:
# santosh_philip AT yahoo DOT com
# Please send all bug reports, enhancement proposals, questions and comments to that address.
#
# VERSION: 0.001
"""legacy code from EPlusInterface"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals




DOSSEP = '\r\n'
MACSEP = '\r'
UNIXSEP = '\n'

def getlinesep(astr):
    """returns the line seperators used in the string astr
    mac is '\r'
    dos is '\r\n'
    unix is '\n'"""
    lsep = None
    if len(astr) == 0:
        lsep = None
    # rcount = string.count(astr,'\r')
    rcount = astr.count('\r')
    # ncount = string.count(astr,'\n')
    ncount = astr.count('\n')
    if ncount == rcount == 0:
        lsep = None
    if ncount == 0:
        lsep = '\r'
    if rcount == 0:
        lsep = '\n'
    if ncount == rcount:
        lsep = '\r\n'
    return lsep

