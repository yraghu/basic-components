#!/usr/bin/env python
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components DataWriter.
# 
# REDHAWK Basic Components DataWriter is free software: you can redistribute it and/or modify it under the terms of 
# the GNU Lesser General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components DataWriter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#
#
# AUTO-GENERATED CODE.  DO NOT MODIFY!
#
# Source: DataWriter.spd.xml
from ossie.cf import CF, CF__POA
from ossie.utils import uuid

from ossie.resource import Resource
from ossie.properties import simple_property

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
            if (state == NOOP):
                # If there was no data to process sleep to avoid spinning
                time.sleep(self.pause)

class DataWriter_base(CF__POA.Resource, Resource):
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
            self.port_dataFloat = bulkio.InFloatPort("dataFloat", maxsize=self.DEFAULT_QUEUE_SIZE)

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

        port_dataFloat = providesport(name="dataFloat",
                                      repid="IDL:BULKIO/dataFloat:1.0",
                                      type_="data")

        ######################################################################
        # PROPERTIES
        # 
        # DO NOT ADD NEW PROPERTIES HERE.  You can add properties in your derived class, in the PRF xml file
        # or by using the IDE.
        filename = simple_property(id_="filename",
                                   type_="string",
                                   mode="readwrite",
                                   action="external",
                                   kinds=("configure",)                                 )
        write = simple_property(id_="write",
                                type_="boolean",
                                defvalue=True,
                                mode="readwrite",
                                action="external",
                                kinds=("configure",),
                                description="""Enables (default) or disables writing data out to a file"""
                                )
        overwrite = simple_property(id_="overwrite",
                                    type_="boolean",
                                    defvalue=False,
                                    mode="readwrite",
                                    action="external",
                                    kinds=("configure",),
                                    description="""If enabled, will cause DataWriter to overwrite [filename] if it already exists. Otherwise DataWriter will generate a non-preexisting name to use (appends to [filename] until an unused name is found)"""
                                    )
        endian = simple_property(id_="endian",
                                 type_="string",
                                 defvalue="little",
                                 mode="readwrite",
                                 action="external",
                                 kinds=("configure",),
                                 description="""Set endianness of data in destination file"""
                                 )

