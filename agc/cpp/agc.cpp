/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this
 * source distribution.
 *
 * This file is part of REDHAWK Basic Components agc.
 *
 * REDHAWK Basic Components agc is free software: you can redistribute it and/or modify it under the terms of
 * the GNU Lesser General Public License as published by the Free Software Foundation, either
 * version 3 of the License, or (at your option) any later version.
 *
 * REDHAWK Basic Components agc is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License along with this
 * program.  If not, see http://www.gnu.org/licenses/.
 */

/**************************************************************************

    This is the component code. This file contains the child class where
    custom functionality can be added to the component. Custom
    functionality to the base class can be extended here. Access to
    the ports can also be done from this class

**************************************************************************/

#include "agc.h"

PREPARE_LOGGING(agc_i)

agc_i::agc_i(const char *uuid, const char *label) :
    agc_base(uuid, label),
    realAgc(NULL),
    cmplxAgc(NULL)
{
	//set up the listeners - when the properties change call our callback
	std::string s = "alpha";
	setPropertyChangeListener(s, this, &agc_i::propChange);
	s = "avgPower";
	setPropertyChangeListener(s, this, &agc_i::propChange);
	s= "minPower";
	setPropertyChangeListener(s, this, &agc_i::propChange);
	s= "maxPower";
	setPropertyChangeListener(s, this, &agc_i::propChange);
}

agc_i::~agc_i()
{
	flushAGC(false);
}

void agc_i::propChange(const std::string& propStr)
{
	//When a property changes - we must apply the change to the AGC
	agcNeedsUpdate=true;
}

void agc_i::initialize() throw (CF::LifeCycle::InitializeError, CORBA::SystemException)
{
	agc_base::initialize();
	agcNeedsUpdate=true;
}
void agc_i::flushAGC(bool flushStreamID)
{
	//flush the state of the agc
	if (flushStreamID)
		streamID="";
	agcNeedsUpdate=true;
	if(realAgc)
	{
		delete realAgc;
		realAgc=NULL;
	}
	if(cmplxAgc)
	{
		delete cmplxAgc;
		cmplxAgc=NULL;
	}
}

void agc_i::updateAGC(int mode)
{
	if (mode==0)  //real
	{
		if (cmplxAgc)
		{
			delete cmplxAgc;
			cmplxAgc = NULL;
		}
		updateTheAGC(realAgc, realIn, realOut);
	}
	else  //complex
	{
		if (realAgc)
		{
			delete realAgc;
			realAgc = NULL;
		}
		updateTheAGC(cmplxAgc, cmplxIn, cmplxOut);
	}
}

//Templatized method which applies the AGC change to the specific one which is chosen
template<typename T>
void agc_i::updateTheAGC(ExpAgc<float,T>*& agc, std::valarray<T>& in, std::valarray<T>&out)
{
	if (agc!=NULL)
	{
		if (agc->getAlpha()!=alpha)
		{
			alpha = agc->setAlpha(alpha);
		}
		if(agc->getMaxPower()!=maxPower)
		{
			agc->setMaxPower(maxPower);
		}
		if(agc->getMinPower()!=minPower)
		{
			agc->setMinPower(minPower);
		}
	}
	else
	{
		agc = new ExpAgc<float,T>(in, out, avgPower, minPower, maxPower, eps, alpha);
		//in case the alpha value was bad - set the actual one from the agc
		alpha = agc->getAlpha();
	}
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
        (agc_base).
    
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
        setPropertyChangeListener(<property name>, this, &agc_i::<callback method>)
        in the constructor.
            
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            
        //Add to agc.cpp
        agc_i::agc_i(const char *uuid, const char *label) :
            agc_base(uuid, label)
        {
            setPropertyChangeListener("scaleValue", this, &agc_i::scaleChanged);
        }

        void agc_i::scaleChanged(const std::string& id){
            std::cout << "scaleChanged scaleValue " << scaleValue << std::endl;
        }
            
        //Add to agc.h
        void scaleChanged(const std::string&);
        
        
************************************************************************************************/
int agc_i::serviceFunction()
{
	bulkio::InFloatPort::dataTransfer *tmp = dataFloat_in->getPacket(-1);
	if (not tmp) { // No data is available
		return NOOP;
	}

	bool forceSriUpdate = false;
    if (streamID!=tmp->streamID)
    {
    	if (streamID=="")
    	{
    		forceSriUpdate=true;
    		streamID=tmp->streamID;
    	}
    	else
    	{
    		std::cout<<"AGC::WARNING -- pkt streamID "<<tmp->streamID<<" differs from streamID "<< streamID<<". Throw the data on the floor"<<std::endl;
    		delete tmp; //must delete the dataTransfer object when no longer needed
    		return NORMAL;
    	}
    }

	if (tmp->sriChanged || forceSriUpdate)
	{
		//check for swapping from real to complex data
		if (tmp->SRI.mode==1 and cmplxAgc==NULL)
		{
			agcNeedsUpdate=true;
		}
		else if (tmp->SRI.mode==0 and realAgc==NULL)
		{
			agcNeedsUpdate=true;
		}
		dataFloat_out->pushSRI(tmp->SRI);
	}
	if (enabled)
	{
		if (agcNeedsUpdate)
			updateAGC(tmp->SRI.mode);

		outputData.resize(tmp->dataBuffer.size());
		if (realAgc)
		{
			realIn.resize(tmp->dataBuffer.size());
			realOut.resize(tmp->dataBuffer.size());
			for (unsigned int i=0; i<tmp->dataBuffer.size(); i++) {
				realIn[i] = tmp->dataBuffer[i];
			}
			realAgc->process();
			for (unsigned int i=0; i<tmp->dataBuffer.size(); i++) {
				outputData[i] = realOut[i];
			}
		}
		else if(cmplxAgc)
		{
			cmplxIn.resize(tmp->dataBuffer.size()/2);
			cmplxOut.resize(cmplxIn.size());
			for (unsigned int i=0; i<cmplxIn.size(); i++) {
				cmplxIn[i] = std::complex<float>(tmp->dataBuffer[2*i], tmp->dataBuffer[2*i+1]);
			}
			cmplxAgc->process();
			for (unsigned int i=0; i<cmplxOut.size(); i++) {
				outputData[2*i]   = cmplxOut[i].real();
				outputData[2*i+1] = cmplxOut[i].imag();
			}
		}
		else
			std::cout<<"THIS SHOULD NEVER HAPPEN"<<std::endl;
		dataFloat_out->pushPacket(outputData, tmp->T, tmp->EOS, tmp->streamID);
	}
	else
	{
		//if agc is not enabled make sure the agc's are deleted
		//and just pass the output along
		flushAGC(false);
		dataFloat_out->pushPacket(tmp->dataBuffer, tmp->T, tmp->EOS, tmp->streamID);
	}
	if (tmp->EOS)
	{
		flushAGC(true);
	}

	delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
	return NORMAL;
}
