#!/usr/bin/env python

# source @
# https://github.com/bpkempke/kicad-scripts

import sys
from pcbnew import *
import wx
import numpy as np 
 
in_filename=sys.argv[1]
out_filename = sys.argv[2]
net_name = sys.argv[3]
via_spacing = sys.argv[4]
edge_clearance = FromMils(int(sys.argv[5]))
via_type_idx = int(sys.argv[6])
pcb = LoadBoard(in_filename)
 
net_code = pcb.FindNet(net_name).GetNet()

via_dimensions = pcb.GetViasDimensionsList()[via_type_idx]
 
pcb_bounding_box = pcb.ComputeBoundingBox()
left = pcb_bounding_box.GetLeft() + edge_clearance
right = pcb_bounding_box.GetRight() - edge_clearance
top = pcb_bounding_box.GetX() + edge_clearance
bottom = pcb_bounding_box.GetBottom() - edge_clearance

num_x = int(ToMils(right-left)/float(via_spacing))+1
num_y = int(ToMils(bottom-top)/float(via_spacing))+1

for x in np.linspace(left, right, num_x):
    for y in np.linspace(top, bottom, num_y):
        print "adding a via...%f %f"%(x,y)
        new_via = VIA(pcb)
        new_via.SetViaType(VIA_THROUGH)
        new_via.SetPosition(wxPoint(x,y))
        new_via.SetNetCode(net_code)
        new_via.SetWidth(via_dimensions.m_Diameter)
        new_via.SetDrill(via_dimensions.m_Drill)
        pcb.Add(new_via)
         
pcb.Save(out_filename)
