
#ifndef BFIELD_CL
#define BFIELD_CL

#include "constants.cl"
#include "utils.cl"
#include "vector_funcs.cl"
#include "particle_props.cl"

// Uniform test field
static float4 GetUniformField(void)
{
    // Similar strength to Earth's field
    float4 B;
    B.x = 0.;
    B.y = 0.;
    B.z = BMAG;
    B.w = BMAG;
    return B;
}


// Dipole Approx from AERIE Code:
// aerie/trunk/src/astro-service/src/GeoDipoleService.cc
static float4 GetField(float4 pos)
{
    float r = vec_three_Mag(pos)/E_r_m; //EquatorialRadius (meters)
    float B0 = 31.2 * 1e-6; // micro Tesla
    float tilt = 11.5*PI/180;//DEG2RAD; // deg to rad

    float xp = pos.x;
    float yp = pos.y*cos(tilt) - pos.z*sin(tilt);
    float zp = pos.y*sin(tilt) + pos.z*cos(tilt);
    float rp = sqrt(xp*xp + yp*yp + zp*zp);

    float theta = acos(zp/rp);
    float phi = atan2(yp,xp);

    float r3 = r*r*r;
    float Br = -2*B0*(1./r3)*cos(theta);
    float Btheta = -B0*(1./r3)*sin(theta);
    
    float4 B;
    B.x = sin(theta)*cos(phi)*Br + cos(theta)*cos(phi)*Btheta;
    B.y = sin(theta)*sin(phi)*Br + cos(theta)*sin(phi)*Btheta;
    B.z = cos(theta)*Br - sin(theta)*Btheta;

    B.w = vec_three_Mag(B);
    return B;
}



// http://hanspeterschaub.info/Papers/UnderGradStudents/MagneticField.pdf
__constant int NCoeff = 13;
__constant int Coeff_Ind[104][2] =
 {{1, 0}, {1, 1}, {2, 0}, {2, 1}, {2, 2}, {3, 0}, {3, 1}, {3, 2}, {3, 3}, {4, 0}, {4, 1}, {4, 2}, {4, 3}, {4, 4}, {5, 0}, {5, 1}, {5, 2}, {5, 3}, {5, 4}, {5, 5},
  {6, 0}, {6, 1}, {6, 2}, {6, 3}, {6, 4}, {6, 5}, {6, 6}, {7, 0}, {7, 1}, {7, 2}, {7, 3}, {7, 4}, {7, 5}, {7, 6}, {7, 7}, {8, 0}, {8, 1}, {8, 2}, {8, 3}, {8, 4}, {8, 5}, {8, 6}, {8, 7}, {8, 8},
  {9, 0}, {9, 1}, {9, 2}, {9, 3}, {9, 4}, {9, 5}, {9, 6}, {9, 7}, {9, 8}, {9, 9}, {10, 0}, {10, 1}, {10, 2}, {10, 3}, {10, 4}, {10, 5}, {10, 6}, {10, 7}, {10, 8}, {10, 9}, {10, 10}, {11, 0},  {11, 1},
  {11, 2}, {11, 3}, {11, 4}, {11, 5}, {11, 6}, {11, 7}, {11, 8}, {11, 9}, {11, 10}, {11, 11}, {12, 0}, {12, 1}, {12, 2}, {12, 3}, {12, 4}, {12, 5}, {12, 6}, {12, 7}, {12, 8}, {12, 9}, {12, 10}, {12, 11},
  {12, 12}, {13, 0}, {13, 1}, {13, 2}, {13, 3}, {13, 4}, {13, 5}, {13, 6}, {13, 7}, {13, 8}, {13, 9}, {13, 10}, {13, 11}, {13, 12}, {13, 13}};


// Coeff calc from semi-normed coeff from http://www.ngdc.noaa.gov/IAGA/vmod/igrf12coeffs.txt
//2015 g SV 
__constant float gCoeff[104][2] =
  {{-29442, 10.3}, {-1501, 18.1}, {-3667.6, -13.05}, {5218.5, -5.7158}, {1452.1, 1.8187}, {3376.8, 8.5}, {-7202.4, -16.84}, {2373.4, -1.3555}, {460.11, -7.9848}, 
   {3970.8, -3.0625}, {4503, 1.1068}, {471.14, -35.609}, {-700.49, 8.5758}, {52.062, -3.1799}, {-1831.7, -1.575}, {3661, 5.0833}, {1478.6, -9.9908}, {-663.11, -0.47062}, 
   {-349.42, 3.1059}, {2.8764, 2.7361}, {1010.6, -4.3312}, {1279.7, -1.8903}, {1086.4, -10.461}, {-1294.2, 20.922}, {-157.7, -6.5482}, {30.714, 0.69804}, {-47.623, 1.0747},
   {2187.9, 8.0437}, {-2699.2, -7.0939}, {-196.93, -14.48}, {1060.8, 26.622}, {185.23, 1.2349}, {58.04, -3.7047}, {-6.7811, -1.9375}, {4.4014, 0.12945}, {1216.6, 10.055},
   {589.88, 0.0}, {-947.79, -33.649}, {-132.54, 20.71}, {-550.77, -5.3472}, {198.73, 5.9322}, {80.323, 0.68652}, {-39.859, -1.0027}, {-1.2534, 0.18801}, {512.79, 0.0}, {1121.2, 0.0},
   {336.82, 0.0}, {-273.84, 0.0}, {39.463, 0.0}, {-448.09, 0.0}, {-1.7398, 0.0}, {65.542, 0.0}, {-23.514, 0.0}, {-6.395, 0.0}, {-342.81, 0.0}, {-1532.7, 0.0}, {21.069, 0.0}, {82.64, 0.0},
   {-58.435, 0.0}, {133.05, 0.0}, {-28.924, 0.0}, {42.091, 0.0}, {19.638, 0.0}, {-4.7786, 0.0}, {-2.1371, 0.0}, {1067.8, 0.0}, {-699.58, 0.0}, {-940.81, 0.0}, {655.94, 0.0}, {-191.61, 0.0},
   {95.054, 0.0}, {-65.882, 0.0}, {9.9209, 0.0}, {38.692, 0.0}, {-1.763, 0.0}, {1.0881, 0.0}, {2.0299, 0.0}, {-1254.4, 0.0}, {-179.41, 0.0}, {318.05, 0.0}, {779.06, 0.0}, {-389.53, 0.0},
   {300.62, 0.0}, {20.83, 0.0}, {58.527, 0.0}, {-17.558, 0.0}, {-10.217, 0.0}, {1.8865, 0.0}, {-2.5033, 0.0}, {0.0, 0.0}, {0.0, 0.0}, {-1557.2, 0.0}, {619.01, 0.0}, {641.57, 0.0},
   {-492.06, 0.0}, {695.88, 0.0}, {-90.309, 0.0}, {213.71, 0.0}, {-14.279, 0.0}, {20.422, 0.0}, {2.8388, 0.0}, {5.0184, 0.0}, {-1.1355, 0.0}, {-0.16702, 0.0}};

//2015 h SV 
__constant float hCoeff[104][2] =
  {{0.0, 0.0}, {4797.1, -26.6}, {0.0, 0.0}, {-4928.7, -47.458}, {-555.9, -12.211}, {0.0, 0.0}, {-353.03, 25.107}, {474.25, -0.7746}, {-425.64, 1.423}, {0.0, 0.0}, {1567.8, -7.1942}, {-738.41, 20.74},
   {378.38, 6.0658}, {-243.67, -3.8455}, {0.0, 0.0}, {480.88, 6.0999}, {1514, 13.065}, {-561.45, -5.6475}, {35.496, 7.543}, {70.296, 0.0}, {0.0, 0.0}, {-393.18, 0.0}, {496.15, -31.383}, {586.81, -6.974},
   {-363.97, 1.0914}, {16.986, 2.0941}, {42.048, 0.67169}, {0.0, 0.0}, {-1918.9, 28.376}, {-564.74, 11.584}, {116.73, -4.0957}, {301.31, -3.7047}, {20.993, -3.7047}, {-66.358, 0.24218}, {-1.424, -0.12945},
   {0.0, 0.0}, {677.02, -20.109}, {-1026.3, 16.825}, {550.88, 4.142}, {-390.35, 13.368}, {240.26, -2.9661}, {39.132, -2.0596}, {-22.812, 0.75205}, {1.3161, 0.0}, {0.0, 0.0}, {-2751.9, 0.0}, {1173.4, 0.0},
   {979.2, 0.0}, {-383.36, 0.0}, {-232.47, 0.0}, {135.7, 0.0}, {7.5335, 0.0}, {-10.336, 0.0}, {5.116, 0.0}, {0.0, 0.0}, {778.52, 0.0}, {-84.277, 0.0}, {760.29, 0.0}, {514.23, 0.0}, {-583.93, 0.0},
   {-24.792, 0.0}, {-84.181, 0.0}, {-22.911, 0.0}, {-3.1857, 0.0}, {-5.1646, 0.0}, {0.0, 0.0}, {-46.639, 0.0}, {818.1, 0.0}, {-229.58, 0.0}, {-263.47, 0.0}, {126.74, 0.0}, {-18.824, 0.0}, {-109.13, 0.0},
   {-31.864, 0.0}, {-22.037, 0.0}, {-5.4407, 0.0}, {-1.392, 0.0}, {0.0, 0.0}, {-986.73, 0.0}, {318.05, 0.0}, {1233.5, 0.0}, {-1071.2, 0.0}, {100.21, 0.0}, {145.81, 0.0}, {-11.705, 0.0}, {17.558, 0.0},
   {5.1087, 0.0}, {-8.4892, 0.0}, {-0.27815, 0.0}, {0.39744, 0.0}, {0.0, 0.0}, {-1557.2, 0.0}, {619.01, 0.0}, {2053, 0.0}, {-492.06, 0.0}, {-835.05, 0.0}, {-45.155, 0.0}, {106.86, 0.0}, {-14.279, 0.0},
   {27.229, 0.0}, {14.194, 0.0}, {-3.011, 0.0}, {-1.1355, 0.0}, {-0.44539, 0.0}};


// IGRF coefficients struct
struct igrf_struct
{
    float days; // Days since Jan 1, 2000 00:00:00
    float gLocal[13][14];
    float hLocal[13][14];
};


// Allocate g,h coeff arrays so not 
// to re-allocated at each time step
static void SetCoeffIndexScheme(struct igrf_struct *coeff_struct)
{
    float days = coeff_struct->days;
    // Get Coefficient Indexing Scheme
    int c_0, c_1;
    for (int i = 0; i < 104; i++)
    {
        c_0 = Coeff_Ind[i][0]-1;
        c_1 = Coeff_Ind[i][1]-1;
        coeff_struct->gLocal[c_0][c_1+1] = gCoeff[i][0] + gCoeff[i][1]*days/365.;
        coeff_struct->hLocal[c_0][c_1+1] = hCoeff[i][0] + hCoeff[i][1]*days/365.;
    }
}



// Calculate IGRF
// p            = geocentric coords - x,y,z - in units m
// coeff_struct = coefficients struct
// days = decimal days since January 1, 2000
// returns B components in Geocentric Inertial Cartesian Coords - T
//static float4 igrf(float4 p, struct igrf_struct *coeff_struct)
//float4 igrf(float4 p, struct igrf_struct *coeff_struct);
//float4 igrf(float4 p, struct igrf_struct *coeff_struct)
static float4 igrf(float4 p, struct igrf_struct *coeff_struct)
{
    // Position vector in spherical coordinates
    float r = vec_three_Mag(p)/E_r_m;
    float phi = atan2(p.y,p.x);
    float theta = acos(p.z/(r*E_r_m));;

    // Hard set Bsph to zero, avoiding potential zero_vec issues
    float4 Bsph;
    Bsph.x = 0;
    Bsph.y = 0;
    Bsph.z = 0;

    //Avoid Pole Singularities
    theta = MAX(theta,0.0001);
    theta = MIN(theta,PI-.00001);

    // Get Schmidt Quasi-Normalized IGRF Coefficients
    // and Calculate B-Field
    float P11 = 1;
    float P10 = P11;
    float dP11 = 0;
    float dP10 = dP11;
    float P2, P20, dP2, dP20;
    float K = 0;
    float ct = cos(theta);
    float st = sin(theta);
    float cp = cos(phi);
    float sp = sin(phi);
    float c_mp, s_mp, rpow, gl, hl, n_float, m_float;

    for (int m = 0; m < NCoeff+1; m++)
    {
        for (int n = 1; n < NCoeff+1; n++)
        {
            if (m <= n)
            {
                m_float = (float)m;
                n_float = (float)n;
                if (n==m)
                {
                    P2 = st*P11;
                    dP2 = st*dP11 + ct*P11;
                    P11 = P2;
                    P10 = P11;
                    P20 = 0;
                    dP11 = dP2;
                    dP10 = dP11;
                    dP20 = 0;
                }
                else if (n == 1)
                {
                    P2 = ct*P10;
                    dP2 = ct*dP10 - st*P10;
                    P20 = P10;
                    P10 = P2;
                    dP20 = dP10;
                    dP10 = dP2;
                }
                else
                {
                    K = (n_float-1.)*(n_float-1.)-m_float*m_float;
                    K /= (2*n_float-1.)*(2*n_float-3.);
                    P2 = ct*P10 - K*P20;
                    dP2 = ct*dP10 - st*P10 - K*dP20;
                    P20 = P10;
                    P10 = P2;
                    dP20 = dP10;
                    dP10 = dP2;
                }

                rpow = pow(1./r,n+2);
                c_mp = cos(phi*m_float);
                s_mp = sin(phi*m_float);
                gl = coeff_struct->gLocal[n-1][m];
                hl = coeff_struct->hLocal[n-1][m];

                Bsph.x += rpow*(n_float+1.)*(gl*c_mp+hl*s_mp)*P2;
                Bsph.z += rpow*(gl*c_mp+hl*s_mp)*dP2;
                Bsph.y += rpow*m_float*(-gl*s_mp+hl*c_mp)*P2;
 
            }
        }
    }

    Bsph.y /= -st;
    Bsph.z *= -1;
    Bsph.w = Bsph.x;

    // Cartesian B in nanoT
    float4 B;
    B.x = (Bsph.x*st+Bsph.z*ct)*cp-Bsph.y*sp;
    B.y = (Bsph.x*st+Bsph.z*ct)*sp+Bsph.y*cp;
    B.z = Bsph.x*ct-Bsph.z*st;

    // Set units to Tesla
    B = vec_scale(1e-9,B);
    B.w = vec_three_Mag(B);

    return B;
}

#endif // BFIELD_CL
