# CONVERT VASP POSCAR FILE TO ATAT'S STR.OUT FORMAT.
#
# INPUT:
#   lat.in
#   POSCAR
#
# OUTPUT:
#   str.out printed to stdout
#
# ASSUMES:
# 0) YOU HAVE A WORKING INSTALLATION OF ATAT ON YOUR SYSTEM (RELIES ON "cellcvrt)
# 1) YOU HAVE LAT.IN FILE IN THE FOLLOWING FORMAT (TAKEN FROM ATAT MANUAL, TEXT IS MODIFIED A BIT):
#   First, the coordinate system a,b,c is specified as
#   [ax] [ay] [az]
#   [bx] [by] [bz]
#   [cx] [cy] [cz]
#   Then the lattice vectors u,v,w are listed, expressed in the coordinate system just defined:
#   [ua] [ub] [uc]
#   [va] [vb] [vc]
#   [wa] [wb] [wc]
#   Finally, atom positions and types are given, expressed in the same coordinate system
#   as the lattice vectors (i.e. direct/fractional):
#   [atom1a] [atom1b] [atom1c] [atom1types]
#   [atom2a] [atom2b] [atom2c] [atom2types]
#   etc.
#
# 2) YOU HAVE A VASP POSCAR FILE FOR A GIVEN STRUCTURE
#       ****NOTE:****
#       Assumes your POSCAR has a positive "scale" factor (so it is not the total cell volume)
#       I.e., it is a "lattice constant". This is specified in the second line in the POSCAR.
# 
# 3) YOU HAVE A VASP POTCAR FILE FOR THE SAME STRUCTURE

# AUTHOR: Jesper Kristensen, Fall 2013, email: jtk58@cornell.edu
# Last modified November 8 2013.

#!/bin/bash

#===== USER INPUT: SPECIFY NAMES OF FILES
LATIN_IN=lat.in    #WHERE IS YOUR "lat.in"?
POSCAR=POSCAR   #WHERE IS YOUR "POSCAR"?
POTCAR=POTCAR   #WHERE IS YOUR "POTCAR"?
#=====

if [ ! -f "$LATIN_IN" ]; then
    echo "EEEE"
    echo "EEEE POSCAR FILE NOT FOUND IN CURRENT DIRECTORY!"
    echo "EEEE"
    exit
fi
if [ ! -f "$POSCAR" ]; then
    echo "EEEE"
    echo "EEEE POSCAR FILE NOT FOUND IN CURRENT DIRECTORY!"
    echo "EEEE"
    exit
fi
if [ ! -f "$POTCAR" ]; then
    echo "EEEE"
    echo "EEEE POTCAR FILE NOT FOUND IN CURRENT DIRECTORY!"
    echo "EEEE"
    exit
fi

LATIN=lat.in.tmp
cellcvrt -f < $LATIN_IN > $LATIN

#==== FIND BASE LENGTH OF EACH LATTICE VECTOR IN UNIT CELL:
LATINABC=lat.in.abc.tmp
cellcvrt -abc < $LATIN > $LATINABC
SCALES=scales.tmp
head -1 $LATINABC | awk '{ for(i=1;i<=3;i++){print $i} }' > $SCALES

#==== FIND LENGTH OF SUPERCELL LATTICE VECTORS:

#LENGTH OF LATTICE VECTORS OF SUPERCELL:
SUPERSCALES=scales.super.tmp
tmp=tmpp
tmp2=tmpp2

POSCAR_SCALE=`sed -n 2p "$POSCAR"`
sed -n 3,5p "$POSCAR" > $tmp

awk -v len=`echo $POSCAR_SCALE` '{ print sqrt( ($1)*len*($1)*len + ($2)*len*($2)*len + ($3)*len*($3)*len ) }' $tmp > $SUPERSCALES

SCALESCOMPARE=scales.compare.tmp
paste $SCALES $SUPERSCALES > $SCALESCOMPARE

rm -f $SCALES $SUPERSCALES $POSCAR_SCALE

REALSCALES=scales.real.tmp

awk '{ 

len     = ($2)/($1)
lenint  = int( len+0.1 )
delta   = len-lenint
if( delta<0 ){ delta=-delta }

if( delta < 0.01 ){
    #MUST BE AN INTEGER MULTIPLE OF BASE LATTICE VECTOR
    print lenint 
}else{
    #NOT INTEGER MULTIPLE
    print len
}

}' $SCALESCOMPARE > $REALSCALES

rm -f $LATINABC $SCALESCOMPARE 
#SOME TEMPORARY FILE FOR BUILDING str.out:
tmp=tmpp
LABELS=ATOM_LABELS_TMP
#COORDINATE SYSTEM:
head -n +3 "$LATIN" > $tmp

#LATTICE VECTORS:
echo "`sed -n 1p $REALSCALES` 0. 0." >> $tmp
echo "0. `sed -n 2p $REALSCALES` 0." >> $tmp
echo "0. 0. `sed -n 3p $REALSCALES`" >> $tmp

rm -f $REALSCALES

#ATOM LABELS? GET FROM lat.in
#To support multicomponent systems we need to list all atoms in each row and
#then find the unique set (using sort -u):
cat "$LATIN" | tail -n +7 | awk '{ n=split($NF,a,","); for(i=1;i<=n;i++){ print a[i]} }' | sort -u > $LABELS

#NOW GET ATOM LABELS PRESENT IN CURRENT STRUCTURE FROM POTCAR:
POTCAR_LABELS=POTCAR_LABELS
#UPDATE ON FEB 5 2014: INLCUDE "_" IN DELIMITER TO MAKE SURe, e.g., "Zr_sv" GETS MAPPED TO "Zr"
grep -i "VRHFIN =" "${POTCAR}" | awk -F'[:=_]' '{ print $2 }' > $POTCAR_LABELS

awk -v file=$LABELS 'BEGIN{ check="check.tmp" }{

    FOUND=0;
    current=$1;
    while( getline line<file ){
        if(line==current)
        {
            FOUND=1;
        }
    }

    if(FOUND==0){
        exit;
    }

    close(file);

}END{printf("%d", FOUND) > check}' $POTCAR_LABELS
CHECK=`cat check.tmp`

if [ $CHECK -eq 0 ]; then
        echo "EEEE"
        echo "EEEE lat.in ATAT file not consistent with VASP POTCAR file: Atoms exist in POTCAR that are not present in lat.in"
        echo "EEEE"
        exit
fi

#WHERE DO ATOM COORDINATE LISTING START IN POSCAR?
LINENUM=`tail -n +2 "$POSCAR" | grep -inP "^direct" | awk '{ split($0, a, ":"); print a[1]+2}'`

if [[ -z "$LINENUM" ]]
then
    echo "EEEE"
    echo "EEEE Please use \"direct\" listing in your POSCAR."
    echo "EEEE"
    exit
fi

#PRINT ATOM POSITIONS:
POSITIONS=ATOM_POS
awk -v v1=$LINENUM '{ if(NR>=v1){ if(NF>1){ print $0 } } }' "$POSCAR" > $POSITIONS

#PRINT ATOM LABELS:
ATOMS=ATOMS_tmpp #filename for storing atom numbers
awk -v file=$POTCAR_LABELS '{

#Line 6 contains how many atoms sits at each site
if(NR==6){
    n=split($0, a, " ");
}else if(NR>6){
    exit;
}

}END{

    for(k=1;k<=n;k++){
        if(a[k]==0){
            getline line<file;
        }else{
            getline line<file;
            for(j=1;j<=a[k];j++)
                printf("%s\n", line);
        }
    }

}' $POSCAR > $ATOMS

#HOW MANY ATOMIC POSITIONS IN POSCAR?
NUMPOS=`wc -l < $POSITIONS`
#HOW MANY ATOMS?
NUMATS=`wc -l < $ATOMS`

#SANITY CHECK: THEY SHOULD MATCH:
if [ ! "$NUMPOS" -eq "$NUMATS" ]; then
    echo "EEEE"
    echo "EEEE NUMBER OF ATOMIC POSITIONS NOT EQUAL TO NUMBER OF ATOMS IN POSCAR FILE?"
    echo "EEEE"
    exit
fi

#PRINT ATOM POSITIONS AND THEIR LABELS:
paste $POSITIONS $ATOMS >> $tmp
awk '{ for(i=1;i<NF;i++){ printf $i" "}; printf $NF"\n" }' $tmp

#CLEAN UP
rm -rf $tmp $tmp2 $LABELS $POSITIONS $ATOMS $POTCAR_LABELS check.tmp $LATIN
