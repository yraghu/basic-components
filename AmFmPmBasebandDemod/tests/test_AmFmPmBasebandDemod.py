#!/usr/bin/env python
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components AmFmPmBasebandDemod.
# 
# REDHAWK Basic Components AmFmPmBasebandDemod is free software: you can redistribute it and/or modify it under the terms of 
# the GNU Lesser General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components AmFmPmBasebandDemod is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#
import unittest
import ossie.utils.testing
from ossie.utils import sb
import os
from omniORB import any
import math
from ossie.properties import props_from_dict
from math import cos
import time
from ossie.cf import CF
import sys

import cxmodulation

def unpackCx(input):
    output=[]
    for cxVal in input:
        output.append(float(cxVal.real))
        output.append(float(cxVal.imag))
    return output            

#quick helper method for debugging to copy an array into the clipboard
def toClipboard(data):
    import pygtk
    pygtk.require('2.0')
    import gtk
    
    # get the clipboard
    clipboard = gtk.clipboard_get()
    
    clipboard.set_text(str(data))
    
    # make our data available to other applications
    clipboard.store()

class ComponentTests(ossie.utils.testing.ScaComponentTestCase):
    """Test for all component implementations in fcalc"""

    #utility methods to help with SCA set up and tear down for testing

    def setUp(self):
        """Set up the unit test - this is run before every method that starts with test
        """
        ossie.utils.testing.ScaComponentTestCase.setUp(self)
        self.src = sb.DataSource()
        self.sinkAM = sb.DataSink()
        self.sinkPM = sb.DataSink()
        self.sinkFM = sb.DataSink()
        
        #start all my components
        self.startComponent()
        props = {'freqDeviation':10.0,
                 'phaseDeviation':20.0, 
                 'squelch':-2000.0,
                 'debug':False}
        self.comp.configure(props_from_dict(props))
        self.comp.start()
        self.src.start()
        self.sinkAM.start()
        self.sinkPM.start()
        self.sinkFM.start()    
    
    def connect(self,doAm,doFm,doPm):        
        #do the connections
        self.src.connect(self.comp)
        if doAm:
            self.comp.connect(self.sinkAM,'floatIn','am_dataFloat_out')
        if doFm:
            self.comp.connect(self.sinkFM,'floatIn','fm_dataFloat_out')
        if doPm:
            self.comp.connect(self.sinkPM,'floatIn','pm_dataFloat_out')       
    def tearDown(self):
        """Finish the unit test - this is run after every method that starts with test
        """
        self.comp.stop()
        #######################################################################
        # Simulate regular component shutdown
        self.comp.releaseObject()
        self.src.stop()
        self.sinkAM.stop()
        self.sinkFM.stop()
        self.sinkPM.stop()      
        ossie.utils.testing.ScaComponentTestCase.tearDown(self)

    def startComponent(self):
        """Standard start-up for testing the component
        """
        #######################################################################
        # Launch the component with the default execparams
        execparams = self.getPropertySet(kinds=("execparam",), modes=("readwrite", "writeonly"), includeNil=False)
        execparams = dict([(x.id, any.from_any(x.value)) for x in execparams])
        self.launch(execparams)
        
        #######################################################################
        # Verify the basic state of the component
        self.assertNotEqual(self.comp, None)
        self.assertEqual(self.comp.ref._non_existent(), False)
        self.assertEqual(self.comp.ref._is_a("IDL:CF/Resource:1.0"), True)
        #self.assertEqual(self.spd.get_id(), self.comp.ref._get_identifier())
        
        #######################################################################
        # Simulate regular component startup
        # Verify that initialize nor configure throw errors
        #self.comp.initialize()
        configureProps = self.getPropertySet(kinds=("configure",), modes=("readwrite", "writeonly"), includeNil=False)
        self.comp.configure(configureProps)
        
        #######################################################################
        # Validate that query returns all expected parameters
        # Query of '[]' should return the following set of properties
        expectedProps = []
        expectedProps.extend(self.getPropertySet(kinds=("configure", "execparam"), modes=("readwrite", "readonly"), includeNil=True))
        expectedProps.extend(self.getPropertySet(kinds=("allocate",), action="external", includeNil=True))
        props = self.comp.query([])
        props = dict((x.id, any.from_any(x.value)) for x in props)
        # Query may return more than expected, but not less
        for expectedProp in expectedProps:
            self.assertEquals(props.has_key(expectedProp.id), True)
        
        #######################################################################
        # Verify that all expected ports are available
        for port in self.scd.get_componentfeatures().get_ports().get_uses():
            port_obj = self.comp.getPort(str(port.get_usesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a("IDL:CF/Port:1.0"),  True)
            
        for port in self.scd.get_componentfeatures().get_ports().get_provides():
            port_obj = self.comp.getPort(str(port.get_providesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a(port.get_repid()),  True)

    #here are the main test cases and the other helper code given a running environment
    def testAm1(self):
        self.amTest(True,True)
    def testAm2(self):    
        self.amTest(True,False)
    def testAm3(self):
        self.amTest(False,True)
    def testAm4(self):
        self.amTest(False,False)
    def amTest(self,pmConnect, fmConnect):
        """Test sending to port a only
        """
        self.connect(True,fmConnect, pmConnect)
        expected = cxmodulation.getAmTest(100000)
        testInCx = cxmodulation.amBB(expected)
        #print "got %s baseband samples" %len(testInCx)
        testIn = unpackCx(testInCx)
        #print "sending in %s real samples" %len(testIn)
        outAM, outFM, outPM = self.myTestCase(testIn)
        if outAM:
            print "am", len(outAM)
        if outFM:
            print "fm", len(outFM)
        if outPM:
            print "pm", len(outPM)
        sampleDelay = cxmodulation.getFilterDelay(expected,testInCx)
        #print "sampleDelay = %s" %sampleDelay
        #print 
        #toClipboard(expected[sampleDelay:sampleDelay+len(outAM)])
        self.validate(outAM, expected[sampleDelay:sampleDelay+len(outAM)], 1e-5)

    #here are the main test cases and the other helper code given a running environment
    def testPm1(self):
        self.pmTest(True,True)
    def testPm2(self):    
        self.pmTest(True,False)
    def testPm3(self):
        self.pmTest(False,True)
    def testPm4(self):
        self.pmTest(False,False)
    def pmTest(self,amConnect, fmConnect):
        """Test sending to port a only
        """
        self.connect(amConnect,fmConnect, True)
        expected = cxmodulation.getFmTest(100000)
        testInCx = cxmodulation.pmBB(expected)
        #print "got %s baseband samples" %len(testInCx)
        testIn = unpackCx(testInCx)
        #print "sending in %s real samples" %len(testIn)
        outAM, outFM, outPM = self.myTestCase(testIn)
        if outAM:
            print "am", len(outAM)
        if outFM:
            print "fm", len(outFM)
        if outPM:
            print "pm", len(outPM)
        sampleDelay = cxmodulation.getFilterDelay(expected,testInCx)
        #print "sampleDelay = %s" %sampleDelay
        #print 
        self.validate(outPM, [20.0 * x for x in expected[sampleDelay:sampleDelay+len(outPM)]],1e-4)
    
    def testFm1(self):
        self.fmTest(True,True)
    def testFm2(self):    
        self.fmTest(True,False)
    def testFm3(self):
        self.fmTest(False,True)
    def testFm4(self):
        self.fmTest(False,False)
    def fmTest(self,amConnect,pmConnect):
        """Test sending to port a only
        """
        self.connect(amConnect,True, pmConnect)
        expected = cxmodulation.getFmTest(100000)
        testInCx = cxmodulation.fmBB(expected)
        #print "got %s baseband samples" %len(testInCx)
        testIn = unpackCx(testInCx)
        #print "sending in %s real samples" %len(testIn)
        outAM, outFM, outPM = self.myTestCase(testIn)
        if outAM:
            print "am", len(outAM)
        if outFM:
            print "fm", len(outFM)
        if outPM:
            print "pm", len(outPM)
        sampleDelay = cxmodulation.getFilterDelay(expected,testInCx)
        #print "sampleDelay = %s" %sampleDelay
        #print 
        self.validate(outFM, [10.0*x for x in expected[sampleDelay:sampleDelay+len(outFM)]],.1)
       
    def testMultiStream(self):
        """send the same data threw 3 times on 2 streams
           Verify the output is identical for the two unique streams but 
           The second push on the same stream is different due to the state of the demod
        """
        self.connect(False,False,True)
        expected = cxmodulation.getFmTest(8400)
        testInCx = cxmodulation.pmBB(expected)
        testIn = unpackCx(testInCx)
        outAM, outFM, outPM_A = self.myTestCase(testIn, 'streamA')

        outAM, outFM, outPM_B = self.myTestCase(testIn, 'streamB')
        outAM, outFM, outPM_A2 = self.myTestCase(testIn, 'streamA')

        sampleDelay = cxmodulation.getFilterDelay(expected,testInCx)
        #print 
        self.validate(outPM_A, [20.0 * x for x in expected[sampleDelay:sampleDelay+len(outPM_A)]],1e-4)
        self.validate(outPM_A, outPM_B, 1e-5)
        mse = self.getMSE(outPM_A,outPM_A2)                
        self.assertTrue(mse>1.0)

    def testEos(self):
        """send the same data threw 3 times but use Eos to flush the state
           Verify the output is identical after Eos but 
           The second push on the same stream is different due to the state of the demod
        """
        self.connect(False,False,True)
        expected = cxmodulation.getFmTest(8400)
        testInCx = cxmodulation.pmBB(expected)
        testIn = unpackCx(testInCx)
        outAM, outFM, outPM_new1 = self.myTestCase(testIn,eos=True)

        outAM, outFM, outPM_new2 = self.myTestCase(testIn)
        outAM, outFM, outPM_old = self.myTestCase(testIn)

        sampleDelay = cxmodulation.getFilterDelay(expected,testInCx)
        #print 
        self.validate(outPM_new1, [20.0 * x for x in expected[sampleDelay:sampleDelay+len(outPM_new1)]],1e-4)
        self.validate(outPM_new1, outPM_new2, 1e-5)
        mse = self.getMSE(outPM_new1,outPM_old)                
        self.assertTrue(mse>1.0)
                
    def myTestCase(self, data, streamID="test_stream", eos=False):
        """The main engine for all the test cases - configure the equation, push data, and get output
           As applicable
        """
        if data:
            self.src.push(data, EOS = eos, streamID = streamID)
        #data processing is asynchronos - so wait until the data is all processed
        count=0
        outAM = []
        outFM = []
        outPM = []
        while True:
            try:
                thisOutAM =  self.sinkAM.getData()
            except:
                thisOutAM = None
            try:
                thisOutFM =  self.sinkFM.getData()
            except:
                thisOutFM = None
            try:
                thisOutPM =  self.sinkPM.getData()
            except:
                thisOutPM = None
            if thisOutAM:
                outAM.extend(thisOutAM)
            if thisOutFM:
                outFM.extend(thisOutFM)
            if thisOutPM:
                outPM.extend(thisOutPM)
            if thisOutAM or thisOutFM or thisOutPM:
                count=0
            if count==25:
                break
            time.sleep(.01)
            count+=1        
        return outAM, outFM, outPM
    def validate(self, output, input,thresh):
        meanError = self.getMSE(input,output)
        self.assertTrue(meanError<thresh)

    def getMSE(self, output, input):
        self.assertEqual(len(output),len(input))
        sumError = sum([abs(x-y) for x, y in zip(output,input)])
        meanError = sumError/ len(output)
        return meanError
        #print [(x, y) for x, y in zip(output,input[:10])]

                
            
        
if __name__ == "__main__":
    ossie.utils.testing.main("../AmFmPmBasebandDemod.spd.xml") # By default tests all implementations
