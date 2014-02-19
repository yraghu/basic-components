/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this
 * source distribution.
 *
 * This file is part of REDHAWK Basic Components fastfilter.
 *
 * REDHAWK Basic Components fastfilter is free software: you can redistribute it and/or modify it under the terms of
 * the GNU General Public License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * REDHAWK Basic Components fastfilter is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with this
 * program.  If not, see http://www.gnu.org/licenses/.
 */

/**************************************************************************

    This is the component code. This file contains the child class where
    custom functionality can be added to the component. Custom
    functionality to the base class can be extended here. Access to
    the ports can also be done from this class

**************************************************************************/

#include "fastfilter.h"

PREPARE_LOGGING(fastfilter_i)

fastfilter_i::fastfilter_i(const char *uuid, const char *label) :
    fastfilter_base(uuid, label),
    filter_(fftSize, realIn, complexIn, realOut, complexOut)
{
	setPropertyChangeListener("fftSize", this, &fastfilter_i::fftSizeChanged);
	setPropertyChangeListener("filterComplex", this, &fastfilter_i::filterChanged);
	setPropertyChangeListener("filterCoeficients", this, &fastfilter_i::filterChanged);
}

fastfilter_i::~fastfilter_i()
{
}

/***********************************************************************************************

    Basic functionality:

        The service function is called by the serviceThread object (of type ProcessThread).
        This call happens immediately after the previous call if the return value for
        the previous call was NORMAL.
        If the return value for the previous call was NOOP, then the serviceThread waits
        an amount of time defined in the serviceThread's constructor.
        
    SRI:
        To create a StreamSRI object, use the following code:
                std::string stream_id = "testStream";
                BULKIO::StreamSRI sri = bulkio::sri::create(stream_id);

	Time:
	    To create a PrecisionUTCTime object, use the following code:
                BULKIO::PrecisionUTCTime tstamp = bulkio::time::utils::now();

        
    Ports:

        Data is passed to the serviceFunction through the getPacket call (BULKIO only).
        The dataTransfer class is a port-specific class, so each port implementing the
        BULKIO interface will have its own type-specific dataTransfer.

        The argument to the getPacket function is a floating point number that specifies
        the time to wait in seconds. A zero value is non-blocking. A negative value
        is blocking.  Constants have been defined for these values, bulkio::Const::BLOCKING and
        bulkio::Const::NON_BLOCKING.

        Each received dataTransfer is owned by serviceFunction and *MUST* be
        explicitly deallocated.

        To send data using a BULKIO interface, a convenience interface has been added 
        that takes a std::vector as the data input

        NOTE: If you have a BULKIO dataSDDS port, you must manually call 
              "port->updateStats()" to update the port statistics when appropriate.

        Example:
            // this example assumes that the component has two ports:
            //  A provides (input) port of type bulkio::InShortPort called short_in
            //  A uses (output) port of type bulkio::OutFloatPort called float_out
            // The mapping between the port and the class is found
            // in the component base class header file

            bulkio::InShortPort::dataTransfer *tmp = short_in->getPacket(bulkio::Const::BLOCKING);
            if (not tmp) { // No data is available
                return NOOP;
            }

            std::vector<float> outputData;
            outputData.resize(tmp->dataBuffer.size());
            for (unsigned int i=0; i<tmp->dataBuffer.size(); i++) {
                outputData[i] = (float)tmp->dataBuffer[i];
            }

            // NOTE: You must make at least one valid pushSRI call
            if (tmp->sriChanged) {
                float_out->pushSRI(tmp->SRI);
            }
            float_out->pushPacket(outputData, tmp->T, tmp->EOS, tmp->streamID);

            delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
            return NORMAL;

        If working with complex data (i.e., the "mode" on the SRI is set to
        true), the std::vector passed from/to BulkIO can be typecast to/from
        std::vector< std::complex<dataType> >.  For example, for short data:

            bulkio::InShortPort::dataTransfer *tmp = myInput->getPacket(bulkio::Const::BLOCKING);
            std::vector<std::complex<short> >* intermediate = (std::vector<std::complex<short> >*) &(tmp->dataBuffer);
            // do work here
            std::vector<short>* output = (std::vector<short>*) intermediate;
            myOutput->pushPacket(*output, tmp->T, tmp->EOS, tmp->streamID);

        Interactions with non-BULKIO ports are left up to the component developer's discretion

    Properties:
        
        Properties are accessed directly as member variables. For example, if the
        property name is "baudRate", it may be accessed within member functions as
        "baudRate". Unnamed properties are given a generated name of the form
        "prop_n", where "n" is the ordinal number of the property in the PRF file.
        Property types are mapped to the nearest C++ type, (e.g. "string" becomes
        "std::string"). All generated properties are declared in the base class
        (fastfilter_base).
    
        Simple sequence properties are mapped to "std::vector" of the simple type.
        Struct properties, if used, are mapped to C++ structs defined in the
        generated file "struct_props.h". Field names are taken from the name in
        the properties file; if no name is given, a generated name of the form
        "field_n" is used, where "n" is the ordinal number of the field.
        
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            //  - A boolean called scaleInput
              
            if (scaleInput) {
                dataOut[i] = dataIn[i] * scaleValue;
            } else {
                dataOut[i] = dataIn[i];
            }
            
        A callback method can be associated with a property so that the method is
        called each time the property value changes.  This is done by calling 
        setPropertyChangeListener(<property name>, this, &fastfilter_i::<callback method>)
        in the constructor.
            
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            
        //Add to fastfilter.cpp
        fastfilter_i::fastfilter_i(const char *uuid, const char *label) :
            fastfilter_base(uuid, label)
        {
            setPropertyChangeListener("scaleValue", this, &fastfilter_i::scaleChanged);
        }

        void fastfilter_i::scaleChanged(const std::string& id){
            std::cout << "scaleChanged scaleValue " << scaleValue << std::endl;
        }
            
        //Add to fastfilter.h
        void scaleChanged(const std::string&);
        
        
************************************************************************************************/
int fastfilter_i::serviceFunction()
{
    LOG_DEBUG(fastfilter_i, "serviceFunction() example log message");

    bulkio::InFloatPort::dataTransfer *tmp = dataFloat_in->getPacket(bulkio::Const::BLOCKING);
	if (not tmp) { // No data is available
		return NOOP;
	}
    bool forceSriPush = false;
    if (tmp->SRI.mode==1)
    {
    	//unpack the data into a complex vector
    	complexIn.resize(tmp->dataBuffer.size()/2);
    	for (size_t i=0; i!= complexIn.size(); i++)
    	{
    		complexIn[i] = std::complex<float>(tmp->dataBuffer[2*i], tmp->dataBuffer[2*i+1]);
    	}
    	//run the filter
    	filter_.newComplexData();
    	//demux the complex vector to our real output vector
    	cxOutputToReal();
    }
    else
    {
    	//asign the new vector becaus of the allocator issue - it is just easier to copy the data
    	realIn.assign(tmp->dataBuffer.begin(), tmp->dataBuffer.end());
    	//filter the data
    	filter_.newRealData();
    	//we might have a single complex frame if the previous data was complex and there were
    	//complex data still in the filter taps
    	if (!complexOut.empty())
    	{
    		tmp->SRI.mode=1;
    		cxOutputToReal();
    		forceSriPush = true;
    	}
    }

	//to do -- adjust time stamps appropriately on all these output pushes
    // NOTE: You must make at least one valid pushSRI call
    if (tmp->sriChanged || forceSriPush) {
    	dataFloat_out->pushSRI(tmp->SRI);
    }
    if (!complexOutAsReal.empty())
    {
    	dataFloat_out->pushPacket(complexOutAsReal, tmp->T, tmp->EOS, tmp->streamID);
    	complexOutAsReal.clear();
    }
    if (!realOut.empty())
    {
    	if (forceSriPush)
    	{
    		//change mode back to 0 and send another sri
    		tmp->SRI.mode=0;
    		dataFloat_out->pushSRI(tmp->SRI);
    	}
    	dataFloat_out->pushPacket(realOut, tmp->T, tmp->EOS, tmp->streamID);
    	realOut.clear();
    }
    delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
    return NORMAL;
}

void fastfilter_i::cxOutputToReal()
{
	complexOutAsReal.resize(complexOut.size()*2);
	for (size_t i=0; i!= complexOut.size(); i++)
	{
		complexOutAsReal[2*i] = complexOut[i].real();
		complexOutAsReal[2*i+1] = complexOut[i].imag();
	}
	complexOut.clear();
}

void fastfilter_i::fftSizeChanged(const std::string& id)
{
	filter_.setFftSize(fftSize);
}

void fastfilter_i::filterChanged(const std::string& id)
{
    if (filterComplex)
    {
    	ComplexFFTWVector taps(filterCoeficients.size()/2);
    	for (size_t i =0; i!=taps.size(); i++)
    	{
    		taps[i] = std::complex<float>(filterCoeficients[2*i], filterCoeficients[2*i+1]);
    	}
    	filter_.setTaps(taps);
    }
    else
    {
    	RealFFTWVector taps(filterCoeficients.size());
    	copy(filterCoeficients.begin(), filterCoeficients.end(), taps.begin());
    	filter_.setTaps(taps);
    }
}
