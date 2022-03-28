Readme for windiskinfo

Purpose
A small python module for getting information about physical and logical disks 
in windows.

Structure
gathers information about disks with with the help of wmi, and adds it to a 
list of Disk objects.

Dependencies
- wmi 
  Necessary for disk meta information retrieval on windows.