#ifndef AUTOCOROLATE_IMPL_H
#define AUTOCOROLATE_IMPL_H

#include "autocorolate_base.h"
#include "DataTypes.h"
#include "Autocorolate.h"

class autocorolate_i;

class autocorolate_i : public autocorolate_base
{
    ENABLE_LOGGING
    public:
        autocorolate_i(const char *uuid, const char *label);
        ~autocorolate_i();
        int serviceFunction();

    private:
          void correlationSizeChanged(const std::string&);
          void inputOverlapChanged(const std::string&);
          void numAveragesChanged(const std::string&);
          void outputTypeChanged(const std::string&);
          void zeroMeanChanged(const std::string&);
          void zeroCenterChanged(const std::string&);
          Autocorolator::OUTPUT_TYPE translateOutputType();

            RealVector realOutput;
            Autocorolator autocorolator;
            bool paramsChanged;
            bool updateCorrelationSize;
            bool updateInputOverlap;
            bool updateNumAverages;
            bool updateOutputType;
            bool updateZeroMean;
            bool updateZeroCenter;
};

#endif
