/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this
 * source distribution.
 *
 * This file is part of REDHAWK Basic Components autocorrelate.
 *
 * REDHAWK Basic Components autocorrelate is free software: you can redistribute it and/or modify it under the terms of
 * the GNU General Public License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * REDHAWK Basic Components autocorrelate is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this
 * program.  If not, see http://www.gnu.org/licenses/.
 */
#include "autocorrelate_base.h"

/*******************************************************************************************

    AUTO-GENERATED CODE. DO NOT MODIFY

    The following class functions are for the base class for the component class. To
    customize any of these functions, do not modify them here. Instead, overload them
    on the child class

******************************************************************************************/

autocorrelate_base::autocorrelate_base(const char *uuid, const char *label) :
    Resource_impl(uuid, label),
    serviceThread(0)
{
    construct();
}

void autocorrelate_base::construct()
{
    Resource_impl::_started = false;
    loadProperties();
    serviceThread = 0;
    
    PortableServer::ObjectId_var oid;
    dataFloat_in = new bulkio::InFloatPort("dataFloat_in");
    oid = ossie::corba::RootPOA()->activate_object(dataFloat_in);
    dataFloat_out = new bulkio::OutFloatPort("dataFloat_out");
    oid = ossie::corba::RootPOA()->activate_object(dataFloat_out);

    registerInPort(dataFloat_in);
    registerOutPort(dataFloat_out, dataFloat_out->_this());
}

/*******************************************************************************************
    Framework-level functions
    These functions are generally called by the framework to perform housekeeping.
*******************************************************************************************/
void autocorrelate_base::initialize() throw (CF::LifeCycle::InitializeError, CORBA::SystemException)
{
}

void autocorrelate_base::start() throw (CORBA::SystemException, CF::Resource::StartError)
{
    boost::mutex::scoped_lock lock(serviceThreadLock);
    if (serviceThread == 0) {
        dataFloat_in->unblock();
        serviceThread = new ProcessThread<autocorrelate_base>(this, 0.1);
        serviceThread->start();
    }
    
    if (!Resource_impl::started()) {
    	Resource_impl::start();
    }
}

void autocorrelate_base::stop() throw (CORBA::SystemException, CF::Resource::StopError)
{
    boost::mutex::scoped_lock lock(serviceThreadLock);
    // release the child thread (if it exists)
    if (serviceThread != 0) {
        dataFloat_in->block();
        if (!serviceThread->release(2)) {
            throw CF::Resource::StopError(CF::CF_NOTSET, "Processing thread did not die");
        }
        serviceThread = 0;
    }
    
    if (Resource_impl::started()) {
    	Resource_impl::stop();
    }
}

CORBA::Object_ptr autocorrelate_base::getPort(const char* _id) throw (CORBA::SystemException, CF::PortSupplier::UnknownPort)
{

    std::map<std::string, Port_Provides_base_impl *>::iterator p_in = inPorts.find(std::string(_id));
    if (p_in != inPorts.end()) {
        if (!strcmp(_id,"dataFloat_in")) {
            bulkio::InFloatPort *ptr = dynamic_cast<bulkio::InFloatPort *>(p_in->second);
            if (ptr) {
                return ptr->_this();
            }
        }
    }

    std::map<std::string, CF::Port_var>::iterator p_out = outPorts_var.find(std::string(_id));
    if (p_out != outPorts_var.end()) {
        return CF::Port::_duplicate(p_out->second);
    }

    throw (CF::PortSupplier::UnknownPort());
}

void autocorrelate_base::releaseObject() throw (CORBA::SystemException, CF::LifeCycle::ReleaseError)
{
    // This function clears the component running condition so main shuts down everything
    try {
        stop();
    } catch (CF::Resource::StopError& ex) {
        // TODO - this should probably be logged instead of ignored
    }

    // deactivate ports
    releaseInPorts();
    releaseOutPorts();

    delete(dataFloat_in);
    delete(dataFloat_out);

    Resource_impl::releaseObject();
}

void autocorrelate_base::loadProperties()
{
    addProperty(correlationSize,
                4096,
                "correlationSize",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(inputOverlap,
                0,
                "inputOverlap",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(numAverages,
                1,
                "numAverages",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(outputType,
                "NORMAL",
                "outputType",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(zeroMean,
                true,
                "zeroMean",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(zeroCenter,
                false,
                "zeroCenter",
                "",
                "readwrite",
                "",
                "external",
                "configure");

}
