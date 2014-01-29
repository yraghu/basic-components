#include <iostream>
#include "ossie/ossieSupport.h"

#include "autocorolate.h"


int main(int argc, char* argv[])
{
    autocorolate_i* autocorolate_servant;
    Resource_impl::start_component(autocorolate_servant, argc, argv);
    return 0;
}
