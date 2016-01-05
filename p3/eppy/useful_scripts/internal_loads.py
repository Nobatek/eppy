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
# along with Eppy.  If not, see <http://www.gnu.org/licenses/>.


"""
I change the value and input method of internal load objects,
To specify a value of watts/SF for lighting or equipment
"""

import argparse
import sys
import platform
from eppy.modeleditor import IDF

pathnameto_eplusscripting = "../../"
sys.path.append(pathnameto_eplusscripting)

# Initialize platform-specific path to .IDD file.
platfm = platform.system()
if platfm == 'Darwin':
    dwn_idd = '/Applications/EnergyPlus-8-1-0/Energy+.idd'


def convert_iptosi(valueip):
    """Return value per square meter, given value per square foot"""
    valuesi = float(valueip)*10.764
    return valuesi


def assign_loads(unitfg, value, loadtp, spacenm):
    if unitfg:
        value = convert_iptosi(value)
    chloads = []
    loadobjs = idfobjs[loadtp]
    for loadobjs in loadobjs:
        if spacenm in loadobjs.Name:
            loadobjs.Watts_per_Zone_Floor_Area = value
            if loadobjs.Design_Level_Calculation_Method != 'Watts/Area':
                loadobjs.Design_Level_Calculation_Method = 'Watts/Area'
                loadobjs.Design_Level = ''
                chloads.append(loadobjs.Name)
    return chloads, value


if __name__ == '__main__':
    # do the argparse stuff
    parser = argparse.ArgumentParser(usage=None, description=__doc__)
    parser.add_argument(
        'idd', action='store', nargs='?', default=dwn_idd,
        help='location of idd file = ./somewhere/eplusv8-0-1.idd \
        (default: Energy+ default install location')
    parser.add_argument(
        'simfile', action='store',
        help='location of idf simulation file = ./somewhere/f1.idf')
    parser.add_argument(
        'val', action='store',
        help='New value of load objects for space type', type=float)
    parser.add_argument(
        '-u', '--unitconv', action='store_true',
        help='Indicates conversion from IP units to SI')
    parser.add_argument(
        'ldtyp', action='store', help='Name of load type to be edited')
    parser.add_argument(
        'spckeywd', action='store',
        help='Keyword of phrase in object names to indicate space type')
    nspace = parser.parse_args()
    iddfile = nspace.idd
    idffile = nspace.simfile
    value = nspace.val
    unitfg = nspace.unitconv
    loadtp = nspace.ldtyp
    spacenm = nspace.spckeywd
    # read the contents of the simulation file for manipulation
    IDF.setiddname(iddfile)
    idfcnts = IDF(idffile)
    idfobjs = idfcnts.idfobjects
    chloads = assign_loads(unitfg, value, loadtp, spacenm)
    idfcnts.saveas(idffile+'_lds.idf')
    print(chloads)
