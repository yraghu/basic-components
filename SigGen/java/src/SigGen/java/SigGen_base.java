/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
 * source distribution.
 * 
 * This file is part of REDHAWK Basic Components SigGen.
 * 
 * REDHAWK Basic Components SigGen is free software: you can redistribute it and/or modify it under the terms of 
 * the GNU Lesser General Public License as published by the Free Software Foundation, either 
 * version 3 of the License, or (at your option) any later version.
 * 
 * REDHAWK Basic Components SigGen is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
 * PURPOSE.  See the GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License along with this 
 * program.  If not, see http://www.gnu.org/licenses/.
 */
package SigGen.java;

import java.util.Properties;

import org.apache.log4j.Logger;

import org.omg.CosNaming.NamingContextPackage.CannotProceed;
import org.omg.CosNaming.NamingContextPackage.InvalidName;
import org.omg.CosNaming.NamingContextPackage.NotFound;
import org.omg.PortableServer.POAPackage.ServantNotActive;
import org.omg.PortableServer.POAPackage.WrongPolicy;

import CF.InvalidObjectReference;

import org.ossie.component.*;
import org.ossie.properties.*;

/**
 * This is the component code. This file contains all the access points
 * you need to use to be able to access all input and output ports,
 * respond to incoming data, and perform general component housekeeping
 *
 * Source: SigGen.spd.xml
 *
 * @generated
 */
public abstract class SigGen_base extends Resource implements Runnable {
    /**
     * @generated
     */
    public final static Logger logger = Logger.getLogger(SigGen_base.class.getName());

    /**
     * Return values for service function.
     */
    public final static int FINISH = -1;
    public final static int NOOP   = 0;
    public final static int NORMAL = 1;

    /**
     * The property frequency
     * rate at which the periodic output waveforms repeat.  This value is ignored for aperiodic waveforms.
     *
     * @generated
     */
    public final DoubleProperty frequency =
        new DoubleProperty(
            "frequency", //id
            null, //name
            1000.0, //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    /**
     * The property sample_rate
     * sampling rate for output data.
     *
     * @generated
     */
    public final DoubleProperty sample_rate =
        new DoubleProperty(
            "sample_rate", //id
            null, //name
            5000.0, //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    /**
     * The property magnitude
     * amplitude of output data
     *
     * @generated
     */
    public final DoubleProperty magnitude =
        new DoubleProperty(
            "magnitude", //id
            null, //name
            1.0, //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    /**
     * The property shape
     * determine output data type
     *
     * @generated
     */
    public final StringProperty shape =
        new StringProperty(
            "shape", //id
            null, //name
            "sine", //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    /**
     * The property xfer_len
     * number of samples of output data per output packet
     *
     * @generated
     */
    public final LongProperty xfer_len =
        new LongProperty(
            "xfer_len", //id
            null, //name
            1000, //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    /**
     * The property throttle
     * Throttles the output data rate to approximately sample_rate
     *
     * @generated
     */
    public final BooleanProperty throttle =
        new BooleanProperty(
            "throttle", //id
            null, //name
            true, //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    /**
     * The property stream_id
     * bulkio sri streamID for this data source.
     *
     * @generated
     */
    public final StringProperty stream_id =
        new StringProperty(
            "stream_id", //id
            null, //name
            "SigGen Stream", //default value
            Mode.READWRITE, //mode
            Action.EXTERNAL, //action
            new Kind[] {Kind.CONFIGURE} //kind
            );

    // Provides/inputs
    // Uses/outputs
    /**
     * @generated
     */
    public bulkio.OutDoublePort port_out;



    /**
     * @generated
     */
    public SigGen_base()
    {
        super();
        addProperty(frequency);
        addProperty(sample_rate);
        addProperty(magnitude);
        addProperty(shape);
        addProperty(xfer_len);
        addProperty(throttle);
        addProperty(stream_id);

        // Provides/input

        // Uses/output
        this.port_out = new bulkio.OutDoublePort("out");
        this.addPort("out", this.port_out);
    }

    public void start() throws CF.ResourcePackage.StartError
    {
        super.start();
    }

    public void stop() throws CF.ResourcePackage.StopError
    {
        super.stop();
    }

    public void run() 
    {
        while(this.started())
        {
            int state = this.serviceFunction();
            if (state == NOOP) {
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    break;
                }
            } else if (state == FINISH) {
                return;
            }
        }
    }

    protected abstract int serviceFunction();

    /**
     * The main function of your component.  If no args are provided, then the
     * CORBA object is not bound to an SCA Domain or NamingService and can
     * be run as a standard Java application.
     * 
     * @param args
     * @generated
     */
    public static void main(String[] args) 
    {
        final Properties orbProps = new Properties();
        SigGen.configureOrb(orbProps);

        try {
            Resource.start_component(SigGen.class, args, orbProps);
        } catch (InvalidObjectReference e) {
            e.printStackTrace();
        } catch (NotFound e) {
            e.printStackTrace();
        } catch (CannotProceed e) {
            e.printStackTrace();
        } catch (InvalidName e) {
            e.printStackTrace();
        } catch (ServantNotActive e) {
            e.printStackTrace();
        } catch (WrongPolicy e) {
            e.printStackTrace();
        } catch (InstantiationException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        }
    }
}
