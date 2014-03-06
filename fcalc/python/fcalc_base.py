#!/usr/bin/env python
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components fcalc.
# 
# REDHAWK Basic Components fcalc is free software: you can redistribute it and/or modify it under the terms of 
# the GNU Lesser General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components fcalc is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#
#
# AUTO-GENERATED CODE.  DO NOT MODIFY!
#
# Source: fcalc.spd.xml
from ossie.cf import CF, CF__POA
from ossie.utils import uuid

from ossie.resource import Resource
from ossie.properties import simple_property
from ossie.properties import simpleseq_property

import Queue, copy, time, threading
from ossie.resource import usesport, providesport
import bulkio

NOOP = -1
NORMAL = 0
FINISH = 1
class ProcessThread(threading.Thread):
    def __init__(self, target, pause=0.0125):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.target = target
        self.pause = pause
        self.stop_signal = threading.Event()

    def stop(self):
        self.stop_signal.set()

    def updatePause(self, pause):
        self.pause = pause

    def run(self):
        state = NORMAL
        while (state != FINISH) and (not self.stop_signal.isSet()):
            state = self.target()
            delay = 1e-6
            if (state == NOOP):
                # If there was no data to process sleep to avoid spinning
                delay = self.pause
            time.sleep(delay)

class fcalc_base(CF__POA.Resource, Resource):
        # These values can be altered in the __init__ of your derived class

        PAUSE = 0.0125 # The amount of time to sleep if process return NOOP
        TIMEOUT = 5.0 # The amount of time to wait for the process thread to die when stop() is called
        DEFAULT_QUEUE_SIZE = 100 # The number of BulkIO packets that can be in the queue before pushPacket will block

        def __init__(self, identifier, execparams):
            loggerName = (execparams['NAME_BINDING'].replace('/', '.')).rsplit("_", 1)[0]
            Resource.__init__(self, identifier, execparams, loggerName=loggerName)
            self.threadControlLock = threading.RLock()
            self.process_thread = None
            # self.auto_start is deprecated and is only kept for API compatability
            # with 1.7.X and 1.8.0 components.  This variable may be removed
            # in future releases
            self.auto_start = False

        def initialize(self):
            Resource.initialize(self)
            
            # Instantiate the default implementations for all ports on this component
            self.port_a = bulkio.InDoublePort("a", maxsize=self.DEFAULT_QUEUE_SIZE)
            self.port_b = bulkio.InDoublePort("b", maxsize=self.DEFAULT_QUEUE_SIZE)
            self.port_out = bulkio.OutDoublePort("out")

        def start(self):
            self.threadControlLock.acquire()
            try:
                Resource.start(self)
                if self.process_thread == None:
                    self.process_thread = ProcessThread(target=self.process, pause=self.PAUSE)
                    self.process_thread.start()
            finally:
                self.threadControlLock.release()

        def process(self):
            """The process method should process a single "chunk" of data and then return.  This method will be called
            from the processing thread again, and again, and again until it returns FINISH or stop() is called on the
            component.  If no work is performed, then return NOOP"""
            raise NotImplementedError

        def stop(self):
            self.threadControlLock.acquire()
            try:
                process_thread = self.process_thread
                self.process_thread = None

                if process_thread != None:
                    process_thread.stop()
                    process_thread.join(self.TIMEOUT)
                    if process_thread.isAlive():
                        raise CF.Resource.StopError(CF.CF_NOTSET, "Processing thread did not die")
                Resource.stop(self)
            finally:
                self.threadControlLock.release()

        def releaseObject(self):
            try:
                self.stop()
            except Exception:
                self._log.exception("Error stopping")
            self.threadControlLock.acquire()
            try:
                Resource.releaseObject(self)
            finally:
                self.threadControlLock.release()

        ######################################################################
        # PORTS
        # 
        # DO NOT ADD NEW PORTS HERE.  You can add ports in your derived class, in the SCD xml file, 
        # or via the IDE.

        port_a = providesport(name="a",
                              repid="IDL:BULKIO/dataDouble:1.0",
                              type_="data")

        port_b = providesport(name="b",
                              repid="IDL:BULKIO/dataDouble:1.0",
                              type_="data")

        port_out = usesport(name="out",
                            repid="IDL:BULKIO/dataDouble:1.0",
                            type_="control")

        ######################################################################
        # PROPERTIES
        # 
        # DO NOT ADD NEW PROPERTIES HERE.  You can add properties in your derived class, in the PRF xml file
        # or by using the IDE.
        equation = simple_property(id_="equation",
                                   type_="string",
                                   mode="readwrite",
                                   action="external",
                                   kinds=("configure",),
                                   description="""A string representing an equation you want to implement in this component.  "a" represents the data on input a and "b" represents the data on b.  Calculation is performed on a sample by sample basis.
        
                                   An example equation would be "math.sin(a+b)+random.random()"
        
                                   Any operation which is supported in python is supported here.  Furthermore, use the import property to import more modules (including perhpase custom modules with custom functions) """
                                   )
        useAsri = simple_property(id_="useAsri",
                                  type_="boolean",
                                  defvalue=True,
                                  mode="readwrite",
                                  action="external",
                                  kinds=("execparam",),
                                  description="""Use input's A sri as the output sri. False = B"""
                                  )
        import_ = simpleseq_property(id_="import",
                                     type_="string",
                                     defvalue=[
                                                      "math",
                                                      "random",
                                                      ],
                                     mode="readwrite",
                                     action="external",
                                     kinds=("configure",),
                                     description="""python modules (including perhapse custom modules) you want to import to use in your equation"""
                                     )

