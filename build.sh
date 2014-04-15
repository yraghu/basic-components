#!/bin/sh

# Setup environment for Java
if [ -r /usr/share/java-utils/java-functions ]; then
    . /usr/share/java-utils/java-functions
    set_jvm
    export PATH=$JAVA_HOME/bin:$PATH
fi

# Build the DSP library first
make -C dsp -j

# Next build the fftlib library
make -C fftlib -j

# Build components
for dir in agc/cpp AmFmPmBasebandDemod/cpp ArbitraryRateResampler/cpp autocorrelate/cpp \
           BurstDeserializer/cpp DataConverter/DataConverter DataReader/python DataWriter/python \
           fastfilter/cpp fcalc/python freqfilter/python HardLimit/cpp HardLimit/java \
           HardLimit/python medianfilter/python psd/cpp SigGen/cpp \
           SigGen/python SigGen/java sinksocket/cpp sourcesocket/cpp \
           TuneFilterDecimate/cpp unwrap/cpp whitenoise/cpp;
do
    cd $dir
    echo "---------- $dir"
    if [ -x build.sh ]; then
        ./build.sh
    else
        ./reconf
        ./configure
        make -j
    fi
    cd - > /dev/null
done

