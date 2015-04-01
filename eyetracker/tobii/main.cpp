
#include "etr_main.h"
#include "tobiieyetracker.h"

int main(int argc, char * argv[])
{
    return etr_main<TobiiEyetracker>(argc, argv);
}
