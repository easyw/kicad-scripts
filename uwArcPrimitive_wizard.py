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

    def CheckParameters(self):

        pads = self.parameters['Corner']
        

    def GetValue(self):
        name = str(pcbnew.ToMM(self.parameters["Corner"]["width"])) + '_' + str(pcbnew.ToMM(self.parameters["Corner"]["radius"])) + '_' + str((self.parameters["Corner"]["angle"]))
        return "uwArc_%s" % name

    # build a custom pad
    def smdCustomArcPad(self, module, size, pos, rad, name, angle_D):
        pad = D_PAD(module)
        pad.SetSize(pcbnew.wxSize(size[0]/5,size[1]/5))
        pad.SetShape(PAD_SHAPE_CUSTOM) #PAD_RECT)
        pad.SetAttribute(PAD_ATTRIB_SMD) #PAD_SMD)
        #Set only the copper layer without mask
        #since nothing is mounted on these pads
        pad.SetLayerSet( LSET(F_Cu) )
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetPadName(name)
        #pad.Rotate(pos, angle)
        pad.SetAnchorPadShape(PAD_SHAPE_RECT)
        #AddPrimitive(D_PAD self, wxPoint aCenter, wxPoint aStart, int aArcAngle, int aThickness)
        #pad.AddPrimitive(pcbnew.wxPoint(0,pcbnew.FromMM(5)), pcbnew.wxPoint(0,0), 90*10, pcbnew.FromMM(1))
        #pad.AddPrimitive(pcbnew.wxPoint(0,rad), pcbnew.wxPoint(0,0), 90*10, pcbnew.FromMM(1))
        pad.AddPrimitive(pcbnew.wxPoint(0,rad), pcbnew.wxPoint(0,0), int(angle_D), (size[0]))
        #pad.AddPrimitive(pcbnew.wxPoint(0, pcbnew.FromMM(rad)), pcbnew.wxPoint(0,0), 90*10, pcbnew.FromMM(1))
        #pad.AddPrimitive(pos, pcbnew.wxPoint(0,0), angle_D, pcbnew.FromMM(size[0]))
        return pad

    def smdPad(self,module,size,pos,name,ptype,angle_D):
        pad = D_PAD(module)
        pad.SetSize(size)
        pad.SetShape(ptype)  #PAD_SHAPE_RECT PAD_SHAPE_OVAL PAD_SHAPE_TRAPEZOID PAD_SHAPE_CIRCLE
        pad.SetAttribute(PAD_ATTRIB_SMD)
        pad.SetLayerSet(pad.ConnSMDMask())
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetOrientationDegrees(90-angle_D/10)
        pad.SetName(name)
        return pad
        
    def BuildThisFootprint(self):

        pads = self.parameters['Corner']
        
        radius = pads['radius'] #outline['diameter'] / 2
        width = pads['width']
        
        angle_deg = float(pads["angle"]*10)
        angle = math.radians(angle_deg/10) #To radians

        pos = pcbnew.wxPoint(0,0)
        module = self.module
        size_pad = pcbnew.wxSize(width, width)
        #size_pad = pcbnew.wxSize(width/5, width/5)
        module.Add(self.smdCustomArcPad(module, size_pad, pcbnew.wxPoint(0,0), radius, "1", (angle_deg)))
        size_pad = pcbnew.wxSize(width, width)
        end_coord = (radius) * cmath.exp(math.radians(angle_deg/10-90)*1j)
        if pads['rectangle'] or angle_deg == 0:
            module.Add(self.smdPad(module, size_pad, pcbnew.wxPoint(0-width/2,0), "1", PAD_SHAPE_RECT,0))
            pos = pcbnew.wxPoint(end_coord.real+(width/2)*math.cos(angle),end_coord.imag+(width/2)*math.sin(angle)+radius)
            module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_RECT,angle_deg))
        else:
            size_pad = pcbnew.wxSize(width/5, width/5)
            pos = pcbnew.wxPoint(end_coord.real,end_coord.imag+radius)
            module.Add(self.smdPad(module, size_pad, pos, "1", PAD_SHAPE_CIRCLE,0))

        # Text size
        text_size = self.GetTextSize()  # IPC nominal
        thickness = self.GetTextThickness()
        textposy = self.draw.GetLineThickness()/2 + self.GetTextSize()/2 + thickness #+ outline['margin']
        self.draw.Reference( 0, -textposy-width, text_size )
        self.draw.Value( 0, radius+textposy+width, text_size )

uwArcPrimitive_wizard().register()
