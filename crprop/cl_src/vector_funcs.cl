
#ifndef VECTOR_FUNCS_CL
#define VECTOR_FUNCS_CL

#include "constants.cl"
#include "utils.cl"


static float4 vec_sum(const float4 a,
                   const float4 b)
{ 
    return a+b;
}

static float vec_three_dot(const float4 a,
                   const float4 b)
{ 
    float dot_prod = 0.;
    dot_prod += a.x*b.x;
    dot_prod += a.y*b.y;
    dot_prod += a.z*b.z;
    return dot_prod;
}

static float vec_three_Mag(const float4 a)
{ 
    float norm = vec_three_dot(a,a);
    return sqrt(norm);
}

static float4 vec_scale(const float scale,
                   const float4 vec)
{
    float4 svec;
    svec.x = vec.x*scale;
    svec.y = vec.y*scale;
    svec.z = vec.z*scale;
    return svec;
}

static float4 vec_normalize(const float4 a)
{
    float4 nvec;
    float norm = vec_three_Mag(a);
    if (norm > 0.)
    {
        nvec = vec_scale(1./norm,a);
    }

    return nvec;
}

static float4 vec_three_cross(const float4 a, const float4 b)
{
    float4 cross;
    cross.w = 0.0f;
    cross.x = a.y * b.z - b.y * a.z;
    cross.y = b.x * a.z - a.x * b.z;
    cross.z = a.x * b.y - b.x * a.y;
    return cross;
}


static float4 rotate_vec_three_about_axis(const float theta,
                                          const float4 nnaxis,
                                          const float4 origin,
                                          const float4 vec)
{
    if (theta == 0.)
        return vec;

    float4 axis = vec_normalize(nnaxis);

    // From: http://inside.mines.edu/fs_home/gmurray/ArbitraryAxisRotation/
    float ct, st;
    ct = cos(theta);
    st = sin(theta);

    float x, y, z;
    x = vec.x;
    y = vec.y;
    z = vec.z;

    float a, b, c;
    a = origin.x;
    b = origin.y;
    c = origin.z;
    
    float u, v, w;
    u = axis.x;
    v = axis.y;
    w = axis.z;

    float4 rot_vec;
    rot_vec.x = (1-ct)*( a*(v*v+w*w)-u*(b*v+c*w-u*x-v*y-w*z) )+x*ct+(-c*v+b*w-w*y+v*z)*st;
    rot_vec.y = (1-ct)*( b*(u*u+w*w)-v*(a*u+c*w-u*x-v*y-w*z) )+y*ct+(c*u-a*w+w*x-u*z)*st;
    rot_vec.z = (1-ct)*( c*(u*u+v*v)-w*(a*u+b*v-u*x-v*y-w*z) )+z*ct+(-b*u+a*v-v*x+u*y)*st;
    
    return rot_vec;
}

// My spherical cartesian conversion
static float4 sph2cart(float4 sph)
{
    float rcos_theta = sph.x * cos(sph.z);
    float4 X;
    X.x = rcos_theta * cos(sph.y);
    X.y = rcos_theta * sin(sph.y);
    X.z = sph.x * sin(sph.z);
    return X;
}

// spherical to cartesian conversion
static float4 msph2cart(float4 sph)
{
    float4 X;
    float eps = 0.0*DEG2RAD;
    X.x = -sph.y*cos(eps) - sph.x*sin(eps);
    X.y = sph.z;
    X.z = sph.y*sin(eps) - sph.x*cos(eps);
    return X;
}

// tangential spherical to geocentric inertial conversion
// lst = local sidereal time of location - rad
// lat = latitude measured positive toward north from equator - rad
// sph = r,phi,theta spherical coordinate components
static float4 msph2inert(float4 sph, float lst, float lat)
{
    float4 X;
    float Br = sph.x;
    float Bp = sph.y;
    float Bt = sph.z;

    X.x = (Br*cos(lat)+Bt*sin(lat))*cos(lst) - Bp*sin(lst);
    X.y = (Br*cos(lat)+Bt*sin(lat))*sin(lst) + Bp*cos(lst);
    X.z = Br*sin(lat)+Bt*cos(lat);
    //X.x = (Br*sin(lat)+Bt*cos(lat))*cos(lst) - Bp*sin(lst);
    //X.y = (Br*sin(lat)+Bt*cos(lat))*sin(lst) + Bp*cos(lst);
    //X.z = Br*cos(lat)-Bt*sin(lat);

    return X;
}

#endif // VECTOR_FUNCS_CL
