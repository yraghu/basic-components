#!/bin/sh

# Install everything
for dir in dsp fftlib \
           agc/cpp AmFmPmBasebandDemod/cpp ArbitraryRateResampler/cpp autocorrelate/cpp \
           BurstDeserializer/cpp DataConverter/DataConverter DataReader/python DataWriter/python \
           fastfilter/cpp fcalc/python freqfilter/python HardLimit/cpp HardLimit/java \
           HardLimit/python medianfilter/python psd/cpp SigGen/cpp \
           SigGen/python SigGen/java sinksocket/cpp sourcesocket/cpp \
           TuneFilterDecimate/cpp unwrap/cpp whitenoise/cpp;
do
    cd $dir
    echo "---------- $dir"
    make install
    cd - > /dev/null
done

