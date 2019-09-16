#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

# This python script wizard creates an arc track for microwave applications
# Author  easyw
# taskkill -im pcbnew.exe /f &  C:\KiCad-v5-nightly\bin\pcbnew

from __future__ import division

import math, cmath

from pcbnew import *
import pcbnew
import FootprintWizardBase


class uwArcPrimitive_wizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "uW ArcPrimitive Pad"

    def GetDescription(self):
        return "uW ArcPrimitive Pad Footprint Wizard"

    def GenerateParameterList(self):

        self.AddParam("Corner", "width", self.uMM, 1.0)
        self.AddParam("Corner", "radius", self.uMM, 5.0, min_value=0, designator='r', hint="Arc radius")
        self.AddParam("Corner", "angle", self.uDegrees, 90, designator='a')
        self.AddParam("Corner", "rectangle", self.uBool, False)
        self.AddParam("Corner", "solder_clearance", self.uMM, 0.0)
        self.AddParam("Corner", "line", self.uBool, False)

    def CheckParameters(self):

        pads = self.parameters['Corner']
        

    def GetValue(self):
        name = str(pcbnew.ToMM(self.parameters["Corner"]["width"])) + '_' + str(pcbnew.ToMM(self.parameters["Corner"]["radius"])) + '_' + str((self.parameters["Corner"]["angle"]))
        if not self.parameters["Corner"]["line"]:
            pref = "uwArc"
        else:
            pref = "uwLine"
        if self.parameters["Corner"]["rectangle"]:
            pref += "R"
        return pref + "%s" % name
        
    # build a custom pad
    def smdCustomArcPad(self, module, size, pos, rad, name, angle_D, layer, ln):
        pad = D_PAD(module)
        pad.SetSize(pcbnew.wxSize(size[0]/5,size[1]/5))
        pad.SetShape(PAD_SHAPE_CUSTOM) #PAD_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD) #PAD_SMD)
        #pad.SetDrillSize (0.)
        #Set only the copper layer without mask
        #since nothing is mounted on these pads
        pad.SetLayerSet( LSET(layer) )
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetPadName(name)
        #pad.Rotate(pos, angle)
        pad.SetAnchorPadShape(PAD_SHAPE_RECT)
        #AddPrimitive(D_PAD self, wxPoint aCenter, wxPoint aStart, int aArcAngle, int aThickness)
        #pad.AddPrimitive(pcbnew.wxPoint(0,pcbnew.FromMM(5)), pcbnew.wxPoint(0,0), 90*10, pcbnew.FromMM(1))
        #pad.AddPrimitive(pcbnew.wxPoint(0,rad), pcbnew.wxPoint(0,0), 90*10, pcbnew.FromMM(1))
        if not ln:
            pad.AddPrimitive(pcbnew.wxPoint(0,rad), pcbnew.wxPoint(0,0), int(angle_D), (size[0]))
        else:
            pad.AddPrimitive(pcbnew.wxPoint(0,0), pcbnew.wxPoint(rad,0), (size[0]))
        #pad.AddPrimitive(pcbnew.wxPoint(0, pcbnew.FromMM(rad)), pcbnew.wxPoint(0,0), 90*10, pcbnew.FromMM(1))
        #pad.AddPrimitive(pos, pcbnew.wxPoint(0,0), angle_D, pcbnew.FromMM(size[0]))
        return pad

    def smdPad(self,module,size,pos,name,ptype,angle_D,layer):
        pad = D_PAD(module)
        pad.SetSize(size)
        pad.SetShape(ptype)  #PAD_SHAPE_RECT PAD_SHAPE_OVAL PAD_SHAPE_TRAPEZOID PAD_SHAPE_CIRCLE 
        # PAD_ATTRIB_CONN PAD_ATTRIB_SMD
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet( LSET(layer) )
        #pad.SetDrillSize (0.)
        #pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetOrientationDegrees(90-angle_D/10)
        pad.SetName(name)
        return pad
        
    def BuildThisFootprint(self):

        pads = self.parameters['Corner']
        
        radius = pads['radius'] #outline['diameter'] / 2
        width = pads['width']
        sold_clear = pads['solder_clearance']
        line = pads['line']
        
        angle_deg = float(pads["angle"]*10)
        angle = math.radians(angle_deg/10) #To radians

        pos = pcbnew.wxPoint(0,0)
        module = self.module
        size_pad = pcbnew.wxSize(width, width)
        #size_pad = pcbnew.wxSize(width/5, width/5)
        module.Add(self.smdCustomArcPad(module, size_pad, pcbnew.wxPoint(0,0), radius, "1", (angle_deg), F_Cu, line))
        if sold_clear > 0:
            size_pad = pcbnew.wxSize(sold_clear,sold_clear)
            module.Add(self.smdCustomArcPad(module, size_pad, pcbnew.wxPoint(0,0), radius, "1", (angle_deg), F_Mask, line))
        size_pad = pcbnew.wxSize(width, width)
        end_coord = (radius) * cmath.exp(math.radians(angle_deg/10-90)*1j)
        if pads['rectangle'] or angle_deg == 0 or radius == 0:
            if not line:
                module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0-width/2,0), "1", PAD_SHAPE_RECT,0,F_Cu))
            else:
                module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0,0), "1", PAD_SHAPE_RECT,0,F_Cu))
            pos = pcbnew.wxPoint(end_coord.real+(width/2)*math.cos(angle),end_coord.imag+(width/2)*math.sin(angle)+radius)
            if not line:
                module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_RECT,angle_deg,F_Cu))
            else:
                pos = pcbnew.wxPoint(radius,0) #+width/2,0)
                module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_RECT,0,F_Cu))
            if sold_clear > 0:
                size_pad = pcbnew.wxSize(sold_clear,sold_clear)
                if not line:
                    module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0-width/2,0), "1", PAD_SHAPE_RECT,0,F_Mask))
                else:
                    module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0,0), "1", PAD_SHAPE_RECT,0,F_Mask))
                if not line:
                    pos = pcbnew.wxPoint(end_coord.real+(width/2)*math.cos(angle),end_coord.imag+(width/2)*math.sin(angle)+radius)
                    module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_RECT,angle_deg,F_Mask))
                else:
                    pos = pcbnew.wxPoint(radius,0) #+width/2,0)
                    module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_RECT,0,F_Mask))
        else:
            size_pad = pcbnew.wxSize(width/5, width/5)
            if not line:
                pos = pcbnew.wxPoint(end_coord.real,end_coord.imag+radius)
            else:
                pos = pcbnew.wxPoint(radius,0)
            module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_CIRCLE,0,F_Cu))
            #if sold_clear > 0:
            #    size_pad = pcbnew.wxSize(sold_clear,sold_clear)
            #    pos = pcbnew.wxPoint(end_coord.real,end_coord.imag+radius)
            #    module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_CIRCLE,0,F_Mask))

        # Text size
        text_size = self.GetTextSize()  # IPC nominal
        thickness = self.GetTextThickness()
        textposy = self.draw.GetLineThickness()/2 + self.GetTextSize()/2 + thickness #+ outline['margin']
        self.draw.Reference( 0, -textposy-width, text_size )
        if not line:
            self.draw.Value( 0, radius+textposy+width, text_size )
        else:
            self.draw.Value( 0, textposy+width, text_size )

uwArcPrimitive_wizard().register()
