## Creating Wickerlib 
Creating the wickerlib.lib, wickerlib.dcm, and Wickerlib.pretty libraries. 

##### Create a Reference List of Parts

I created an inventory CSV file with the following categories: 

- WBoxSKU
- Reference
- Description
- Value
- KiCadFootprint
- Datasheet
- Package
- MF_Name
- MF_PN
- S1_Name
- S1_PN
- Verified

The file only reads in lines where the Reference is a letter, so it ignores the title line and lines where Reference is a dash or empty.
