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

import pcbnew
import FootprintWizardBase
import PadArray as PA


class uwArc_wizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "uW Arc Pad"

    def GetDescription(self):
        return "uW Arc Pad Footprint Wizard"

    def GenerateParameterList(self):

        self.AddParam("Corner", "width", self.uMM, 1.0)
        self.AddParam("Corner", "radius", self.uMM, 5.0, min_value=0, designator='r', hint="Arc radius")
        self.AddParam("Corner", "angle", self.uDegrees, 90, designator='a')
        self.AddParam("Corner", "rectangle", self.uBool, False)
        #self.AddParam("Corner", "margin", self.uMM, 0.25, min_value=0.2)

    def CheckParameters(self):

        pads = self.parameters['Corner']
        
        # Check that pads do not overlap
        pad_width = pcbnew.ToMM(pads['width'])
        radius = pcbnew.ToMM(pads['radius'])
        angle_deg = float(pads["angle"]*10)
        
        #self.CheckParam("Outline","diameter",min_value=d_min, info="Outline diameter is too small")


    def GetValue(self):
        name = str(pcbnew.ToMM(self.parameters["Corner"]["width"])) + '_' + str(pcbnew.ToMM(self.parameters["Corner"]["radius"]))
        return "uwArc_%s" % name

    def BuildThisFootprint(self):

        pads = self.parameters['Corner']
        
        radius = pads['radius'] #outline['diameter'] / 2
        width = pads['width']
        
        if not pads['rectangle']:
            width = width/2
        pad_size = width
        
        angle_deg = float(pads["angle"]*10)
        angle = math.radians(angle_deg/10) #To radians
        #angle = pads["*angle"]
        
        #numbering = self.parameters['Numbering']
        #outline = self.parameters['Outline']
        #padRotation = self.parameters['Pad rotation']

        if not pads['rectangle']:
            pos = pcbnew.wxPoint(0,0)
        else:
            pos = pcbnew.wxPoint(0-width/2,0)
        #pad_size = pads['width']
        
        #if (pads['radius']) == 0:
        #    pad_shape = pcbnew.PAD_SHAPE_RECT
        #    pads["rectangle"] = True
        #    radius = 0
        #    angle_deg = 0
        #    angle = 0
        #else:
        pad_shape = pcbnew.PAD_SHAPE_RECT if pads["rectangle"] else pcbnew.PAD_SHAPE_OVAL
        pad = PA.PadMaker(self.module).SMDPad(pad_size, pad_size, shape=pad_shape)
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetName('1')
        module = self.module
        module.Add(pad)
        pad = PA.PadMaker(self.module).SMDPad(pad_size, pad_size, shape=pad_shape)
        #pos = pcbnew.wxPoint(radius,radius+width/2) #90deg case
        #start_coord = radius * cmath.exp(math.radians(0-90)*1j)
        #start_coord = (pcbnew.ToMM(start_coord.real), pcbnew.ToMM(start_coord.imag))
        end_coord = (radius) * cmath.exp(math.radians(angle_deg/10-90)*1j)
        #delta_coord = (width/2) * cmath.exp(math.radians(angle_deg/10-90)*1j)
        if not pads['rectangle']:
            pos = pcbnew.wxPoint(end_coord.real,end_coord.imag+radius)
        else:
            pos = pcbnew.wxPoint(end_coord.real+(width/2)*math.cos(angle),end_coord.imag+(width/2)*math.sin(angle)+radius)
        #pos = pcbnew.wxPoint(end_coord.real,end_coord.imag+radius)
        
        pad.SetPos0(pos)
        pad.SetPosition(pos)
        pad.SetOrientationDegrees(90-angle_deg/10)
        pad.SetName('1')
        module = self.module
        module.Add(pad)
        
        # Draw the Track
        self.draw.SetLayer(pcbnew.F_Cu)
        pad_width = pcbnew.ToMM(pads['width'])
        self.draw.SetLineThickness( pads['width'] ) # pcbnew.FromMM( 0.1 ) ) #Default per KLC F5.2 as of 12/2018
        #self.draw.Circle(0, radius, radius)
        self.draw.Arc(0, radius, 0, 0, angle_deg)
        #self.draw.Arc(0+width/2, radius, 0+width/2, 0, angle_deg)
        #self.draw.Arc(0, radius+pad_width/2, 0, 0+pad_width/2, angle_deg)
        #def Arc(self, cx, cy, sx, sy, a):

        # Text size
        
        text_size = self.GetTextSize()  # IPC nominal
        thickness = self.GetTextThickness()
        textposy = radius + self.draw.GetLineThickness()/2 + self.GetTextSize()/2 + thickness #+ outline['margin']
        self.draw.Reference( 0, -2*width, text_size )
        self.draw.Value( 0, textposy+width, text_size )

uwArc_wizard().register()
