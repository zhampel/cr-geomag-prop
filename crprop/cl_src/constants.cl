
#ifndef CONSTANTS_CL
#define CONSTANTS_CL

// Constants and macro functions

#define PI 3.141592653589793238462
#define RAD2DEG (180.0/PI)
#define DEG2RAD (PI/180.0)
#define THETA_MIN 0.001

__constant float speed_of_light = 299792458.; //m/s
__constant float c2 = 299792458.*299792458.;
__constant float E_r = 6371.2; // Earth Radius (km)
__constant float E_r_m = 6378137; // Earth Radius (m)
__constant float inv_E_r = 0.000156956303365143; // Earth Radius (km)
__constant float BMAG = 0.000033; //Tesla

// Zero vector
__constant float4 zero_vec = {0.0f,0.0f,0.0f,0.0f};

#endif // CONSTANTS_CL
