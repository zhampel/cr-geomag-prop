
#ifndef PARTICLE_PROPS_CL
#define PARTICLE_PROPS_CL

#include "constants.cl"
#include "utils.cl"
#include "bfield.cl"
#include "vector_funcs.cl"


// Particle struct
struct particle_struct
{
    float4 pos;  // position vector
    float4 vel;  // velocity vector
    float4 ZMEL; // Charge, mass, energy, lambda (C,kg,eV,[])
    bool alive;   // particle life status
    float time;
};



static float4 AccelFunc(float4 pos, float4 vel)
{
    // Get Magnetic field at pos & calc acceleration
    float4 B = GetUniformField();
    //float4 B = GetField(pos);
    float4 accel = vec_three_cross(vel,B);
    
    return accel;
}

static void PropStepLin(float dt, struct particle_struct *particle)
{
    float4 p = particle->pos;
    float4 v = particle->vel;
    // Get acceleration at p
    float4 accel = AccelFunc(p,v);

    // Time step position
    float4 dx = vec_scale(0.5*dt*dt,accel);
    float4 dvt = vec_scale(dt,v);
    dx = vec_sum(dx,dvt);
    p = vec_sum(p,dx);

    // Time step velocity
    float4 dv = vec_scale(dt,accel);
    v = vec_sum(v,dv);
    particle->pos = p;
    particle->vel = v;
}

static void PropStepRK4(float dt, struct particle_struct *particle)
{
    // http://www.mare.ee/indrek/ephi/nystrom.pdf
    float4 K1, K2, K3, K4;

    float4 p = particle->pos;
    float4 v = particle->vel;

    K1 = AccelFunc(p,v);

    float4 v_hs = vec_scale(0.5*dt,v);
    float4 x_hs = vec_sum(p, v_hs);

    // K2
    float4 k2_x = vec_scale(0.125*dt*dt,K1);
    k2_x = vec_sum(k2_x,x_hs);
    float4 k2_v = vec_scale(0.5*dt,K1);
    k2_v = vec_sum(v,k2_v);
    K2 = AccelFunc(k2_x,k2_v);

    // K3
    float4 k3_x = vec_scale(0.125*dt*dt,K2);
    k3_x = vec_sum(k3_x,x_hs);
    float4 k3_v = vec_scale(0.5*dt,K2);
    k3_v = vec_sum(v,k3_v);
    K3 = AccelFunc(k3_x,k3_v);

    // K4
    float4 k4_x = vec_scale(0.5*dt*dt,K3);
    k4_x = vec_sum(k4_x,x_hs);
    k4_x = vec_sum(k4_x,v_hs);
    float4 k4_v = vec_scale(dt,K3);
    k4_v = vec_sum(v,k4_v);
    K4 = AccelFunc(k4_x,k4_v);

    // Update position
    float4 p_upd = vec_sum(K1,K2);
    p_upd = vec_sum(p_upd,K3);
    p_upd = vec_scale(dt*dt/6,p_upd);
    p_upd = vec_sum(p_upd,v_hs);
    p_upd = vec_sum(p_upd,v_hs);
    p = vec_sum(p,p_upd);

    // Update velocity
    float4 v_upd = vec_sum(K2,K3);
    v_upd = vec_scale(2,v_upd);
    v_upd = vec_sum(v_upd,K1);
    v_upd = vec_sum(v_upd,K4);
    v_upd = vec_scale(dt/6,v_upd);
    v = vec_sum(v,v_upd);
    particle->pos = p;
    particle->vel = v;
}

static void PropStepBoris(float dt, struct particle_struct *particle, struct igrf_struct *coeff_struct)
{
// https://en.wikipedia.org/wiki/Particle-in-cell
// http://e-collection.library.ethz.ch/eserv/eth:5175/eth-5175-01.pdf
// http://www.osti.gov/scitech/servlets/purl/1090047/

    float4 p = particle->pos;
    float4 v = particle->vel;

    float Z = particle->ZMEL.x;
    float mass = particle->ZMEL.y;
    float inv_gamman = 1./particle->ZMEL.w;

    float4 B = igrf(p,coeff_struct);
    //float4 B = GetField(p);
    //float4 B = GetUniformField();

    float q = 0.5*Z*dt*inv_gamman/mass;
    //float q = 0.5*Z*dt/mass;
    float4 h = vec_scale(q,B);
    float hMag2 = vec_three_dot(h,h);

    float4 s = vec_scale(2./(1.+hMag2),h);

    float4 u = v; // v+Q*E where E is electric field

    float4 u_prime = vec_three_cross(u,h);
    u_prime = vec_sum(u,u_prime);
    u_prime = vec_three_cross(u_prime,s);
    u_prime = vec_sum(u,u_prime);


    // Update velocity
    v = u_prime; // u_prime + Q*E

    // Update position
    float4 dx = vec_scale(dt,v);
    particle->vel = v;
    particle->pos = vec_sum(p,dx);
    particle->ZMEL.w = 1./inv_gamman;
    
    // Adding time step
    particle->time += dt;
}

static void PropStepAdaptBoris(float dt, struct particle_struct *particle, struct igrf_struct *coeff_struct)
{
// https://en.wikipedia.org/wiki/Particle-in-cell
// http://e-collection.library.ethz.ch/eserv/eth:5175/eth-5175-01.pdf
// http://www.osti.gov/scitech/servlets/purl/1090047/

    float4 p = particle->pos;
    float4 v = particle->vel;

    float Z = particle->ZMEL.x;
    float mass = particle->ZMEL.y;
    float inv_gamman = 1./particle->ZMEL.w;

    float4 B = igrf(p, coeff_struct);
    //float4 B = GetField(p);
    //float4 B = GetUniformField();
    float Bmag = B.w;

    float dt_theta = 2.*mass*tan(0.5*THETA_MIN)/(Z*Bmag*inv_gamman);
    //float dt_theta = 2.*mass*tan(0.5*THETA_MIN)/(Z*Bmag);
    dt = MIN(dt_theta,dt); 

    float q = 0.5*Z*dt*inv_gamman/mass;
    //float q = 0.5*Z*dt/mass;
    float4 h = vec_scale(q,B);
    float hMag2 = vec_three_dot(h,h);

    float4 s = vec_scale(2./(1.+hMag2),h);

    float4 u = v; // v+Q*E where E is electric field

    float4 u_prime = vec_three_cross(u,h);
    u_prime = vec_sum(u,u_prime);
    u_prime = vec_three_cross(u_prime,s);
    u_prime = vec_sum(u,u_prime);

    // Update velocity
    v = u_prime; // u_prime + Q*E

    // Update position
    float4 dx = vec_scale(dt,v);
    particle->vel = v;
    particle->pos = vec_sum(p,dx);
    particle->ZMEL.w = 1./inv_gamman;
    
    // Adding time step
    particle->time += dt;
}



#endif // PARTICLE_PROPS_CL
