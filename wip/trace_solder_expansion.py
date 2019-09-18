#!/usr/bin/env python

# source @
# https://github.com/bpkempke/kicad-scripts

import sys
from pcbnew import *
import wx
 
 
in_filename=sys.argv[1]
out_filename = sys.argv[2]
net_name = sys.argv[3]
mask_width = sys.argv[4]
mask_layer = sys.argv[5]
pcb = LoadBoard(in_filename)
 
 
ToUnits=ToMils
FromUnits=FromMils
 
 
print "TRACKS WHICH MATCH CRITERIA:"
for item in pcb.GetTracks():
    if type(item) is TRACK and item.GetNetname() == net_name:
         
        start = item.GetStart()
        end = item.GetEnd()
        width = item.GetWidth()
         
        print " * Track: %s to %s, width %f" % (ToUnits(start),ToUnits(end),ToUnits(width))

        new_soldermask_line = DRAWSEGMENT(pcb)
        new_soldermask_line.SetStart(start)
        new_soldermask_line.SetEnd(end)
        new_soldermask_line.SetWidth(FromUnits(int(mask_width)))
        new_soldermask_line.SetLayer(pcb.GetLayerID(mask_layer))
        pcb.Add(new_soldermask_line)
         
pcb.Save(out_filename)
