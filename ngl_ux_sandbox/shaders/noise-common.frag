uniform int dim;
uniform int nb_layers;
uniform int profile;
uniform float time;
uniform vec4 c1;
uniform vec4 c2;
uniform float gain;
uniform float lacunarity;

#if 0
#define FADE(t) t
#elif 0
#define FADE(t) (3.0 - 2.0*t)*t*t               // 3t^2 - 2t^3          (old Perlin)
#else
#define FADE(t) ((6.0*t - 15.0)*t + 10.0)*t*t*t // 6t^5 - 15t^4 + 10t^3 (new Perlin)
#endif

float f(float t) { return FADE(t); }
vec2  f(vec2  t) { return FADE(t); }
vec3  f(vec3  t) { return FADE(t); }
