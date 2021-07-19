#   Converts a 'str.out' file to the VASP POSCAR format.
#
#   Assumes:
#   + You have installed the "ase" python package.
#   + You have the "str2cif" tool from ATAT in your path.
#
# Author: Jesper Kristensen
import  os, sys
from    ase import io

#=== USER SETTINGS:
structure_from  = 'str.out'
structure_to    = 'str.POSCAR'

if not os.path.exists(structure_from):
    print 'EEEE ATAT file %s does not exist in the path!'
    print 'EEEE You have to specify the ATAT file in this Python script.'
    print 'EEEE exiting ...'
    sys.exit(1)

#=== Convert str.out to CIF format first:
print
print 'IIII Converting ATAT to CIF format ...'
tmp = 'tmp.cif'
cmd = 'str2cif < %s > %s' % (structure_from, tmp)
os.system(cmd)

#=== Then convert CIF to POSCAR using ASE:
print 'IIII Converting CIF to POSCAR format ...'
atoms = io.read(tmp)
atoms.write(structure_to, format = 'vasp')

#=== Clean up:
os.remove(tmp)

print 'IIII All done, the resulting POSCAR file is in %s' % structure_to
print

