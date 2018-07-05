

#ifndef UTILS_CL
#define UTILS_CL

#define MAX(a,b) (((a)>(b))?(a):(b))
#define MIN(a,b) (((a)>(b))?(b):(a))


static int my_isnan(float d)
{
  return (d != d);              /* IEEE: only NaN is not equal to itself */
}


static void swap(float *a, float *b)
{
    float temp = *a;
    *a = *b;
    *b = temp;
}


static bool solveQuadratic(const float a, const float b, const float c, float *x0, float *x1)
{
  float discr = b*b - 4*a*c;
  if (discr < 0)
    return false;
  else if (discr == 0)
    *x0 = *x1 = -0.5*b/a;
  else {
    float q = (b > 0) ? -0.5*(b + sqrt(discr)) : -0.5*(b - sqrt(discr));
    *x0 = q/a;
    *x1 = c/q;
  }
  if (*x0 > *x1)
    swap(x0, x1);
  return true;
}


// Input a wavelength value (nm)
// outputs RGB
static float4 Colors(float lambda)
{
    float R, G, B, SSS;

    //nm to RGB
    if (lambda >= 380 && lambda < 440)
    {
        R = -(lambda - 440.) / (440. - 350.);
        G = 0.0;
        B = 1.0;
    }
    else if (lambda >= 440 && lambda < 490)
    {
        R = 0.0;
        G = (lambda - 440.) / (490. - 440.);
        B = 1.0;
    }
    else if (lambda >= 490 && lambda < 510)
    {
        R = 0.0;
        G = 1.0;
        B = -(lambda - 510.) / (510. - 490.);
    }
    else if (lambda >= 510 && lambda < 580)
    {
        R = (lambda - 510.) / (580. - 510.);
        G = 1.0;
        B = 0.0;
    }
    else if (lambda >= 580 && lambda < 645)
    {
        R = 1.0;
        G = -(lambda - 645.) / (645. - 580.);
        B = 0.0;
    }
    else if (lambda >= 645 && lambda <= 780)
    {
        R = 1.0;
        G = 0.0;
        B = 0.0;
    }
    else
    {
        R = 0.0;
        G = 0.0;
        B = 0.0;
    }
    //Intensity Correction
    if (lambda >= 380 && lambda < 420)
        SSS = 0.3 + 0.7*(lambda - 350) / (420 - 350);
    else if (lambda >= 420 && lambda <= 700)
        SSS = 1.0;
    else if (lambda > 700 && lambda <= 780)
        SSS = 0.3 + 0.7*(780 - lambda) / (780 - 700);
    else
        SSS = 0.0;
    SSS *= 255;
    R *= SSS;
    G *= SSS;
    B *= SSS;
    float4 color = {R,G,B,0.0};
    return color;
}

#endif // UTILS_CL
