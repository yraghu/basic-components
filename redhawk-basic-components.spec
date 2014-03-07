# Define default SDRROOT
%{!?_sdrroot:    %define _sdrroot    /var/redhawk/sdr}
%define _prefix    %{_sdrroot}

Name:           redhawk-basic-components
Version:        1.10.0
Release:        1%{?dist}
Summary:        A collection of starter components for REDHAWK
Prefix:         %{_sdrroot}

Group:          Applications/Engineering
License:        LGPLv3+
URL:            http://redhawksdr.org/
Source0:        %{name}-%{version}.tar.gz
Vendor:         REDHAWK

BuildRequires:  redhawk-devel >= 1.10
BuildRequires:  bulkioInterfaces
BuildRequires:  fftw-devel
BuildRequires:  doxygen
Requires:       redhawk >= 1.10
Requires:       bulkioInterfaces
Requires:       scipy
Requires:       fftw

AutoReqProv:    no

%if 0%{?rhel} < 6
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
%endif

%description
A collection of starter components for REDHAWK
 * Commit: __REVISION__
 * Source Date/Time: __DATETIME__

%package devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description devel
Development files for %{name}


%prep
%setup -q


%build
# Setup environment for Java
. /usr/share/java-utils/java-functions && set_jvm
export PATH=$JAVA_HOME/bin:$PATH

# Build the DSP library first
make -C dsp %{?_smp_mflags}

#Next build the fftlib library
make -C fftlib %{?_smp_mflags}

# Build components
for dir in agc/cpp AmFmPmBasebandDemod/cpp ArbitraryRateResampler/cpp autocorrelate/cpp \
           DataConverter/DataConverter DataReader/python DataWriter/python \
           fastfilter/cpp fcalc/python freqfilter/python HardLimit/cpp HardLimit/java \
           HardLimit/python medianfilter/python psd/cpp SigGen/cpp \
           SigGen/python SigGen/java sinksocket/cpp sourcesocket/cpp \
           TuneFilterDecimate/cpp unwrap/cpp whitenoise/cpp;
do
    cd $dir
    ./reconf
    %configure
    make %{?_smp_mflags}
    cd -
done


%install
rm -rf %{buildroot}

# dsp and fftlib aren't autotools projects and don't determine SDRROOT
# automatically
SDRROOT=%{_sdrroot}
export SDRROOT

# Install the libraries and components
for dir in dsp fftlib \
           agc/cpp AmFmPmBasebandDemod/cpp ArbitraryRateResampler/cpp autocorrelate/cpp \
           DataConverter/DataConverter DataReader/python DataWriter/python \
           fastfilter/cpp fcalc/python freqfilter/python HardLimit/cpp HardLimit/java \
           HardLimit/python medianfilter/python psd/cpp SigGen/cpp \
           SigGen/python SigGen/java sinksocket/cpp sourcesocket/cpp \
           TuneFilterDecimate/cpp unwrap/cpp whitenoise/cpp;
do
    make -C $dir install DESTDIR=%{buildroot}
done


%clean
rm -rf %{buildroot}


%files
%defattr(-,redhawk,redhawk,-)
%{_sdrroot}/dom/components/agc
%{_sdrroot}/dom/components/AmFmPmBasebandDemod
%{_sdrroot}/dom/components/ArbitraryRateResampler
%{_sdrroot}/dom/components/autocorrelate
%{_sdrroot}/dom/components/DataConverter
%{_sdrroot}/dom/components/DataReader
%{_sdrroot}/dom/components/DataWriter
%dir %{_sdrroot}/dom/components/dsp
%{_sdrroot}/dom/components/dsp/Release
%{_sdrroot}/dom/components/dsp/dsp.spd.xml
%{_sdrroot}/dom/components/fastfilter
%{_sdrroot}/dom/components/fcalc
%dir %{_sdrroot}/dom/components/fftlib
%{_sdrroot}/dom/components/fftlib/Release
%{_sdrroot}/dom/components/fftlib/fftlib.spd.xml
%{_sdrroot}/dom/components/freqfilter
%{_sdrroot}/dom/components/HardLimit
%{_sdrroot}/dom/components/medianfilter
%{_sdrroot}/dom/components/psd
%{_sdrroot}/dom/components/SigGen
%{_sdrroot}/dom/components/sinksocket
%{_sdrroot}/dom/components/sourcesocket
%{_sdrroot}/dom/components/TuneFilterDecimate
%{_sdrroot}/dom/components/unwrap
%{_sdrroot}/dom/components/whitenoise

%files devel
%defattr(-,redhawk,redhawk,-)
%doc %{_sdrroot}/dom/components/dsp/doc
%{_sdrroot}/dom/components/dsp/inc
%{_sdrroot}/dom/components/fftlib/inc


%changelog
* Tue Mar  4 2014 - 1.9.1-1
- Add new components

* Tue Feb 11 2014 - 1.10.0-6
- Install header files for libraries

* Tue Jul 9 2013 - 1.10.0-1
- Update dependencies for Redhawk 1.9
- Add new components

* Fri Jul 5 2013 - 1.8.5
- Use OpenJDK

* Fri Mar 15 2013 - 1.8.4-3
- Update Java dependency to 1.6

* Tue Mar 12 2013 - 1.8.3-4
- Initial release

