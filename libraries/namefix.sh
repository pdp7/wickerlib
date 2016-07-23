#!/bin/bash

while IFS=, read -r oldname newname; 
do 
  for filename in *.kicad_mod; do
    #echo $filename
  
#  echo $oldname $newname; 
   if [[ $oldname.kicad_mod == $filename ]]
     then 
       echo $oldname;
       mv $oldname.kicad_mod $newname.kicad_mod
       sed -i s/$oldname/$newname/g $newname.kicad_mod
   fi
  done
done

#for filename in *.kicad_mod;
#do
#  echo $filename
#done
#
#echo $filename $oldname $newname
