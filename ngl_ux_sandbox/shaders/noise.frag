#version 100

#define PI 3.14159265358979323846

precision mediump float;
varying vec2 var_tex0_coord;
uniform sampler2D tex0_sampler;
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

float pick1d(float pos, float off)
{
    float value_point = fract(pos + off);
    float value = texture2D(tex0_sampler, vec2(value_point, 0)).x;
    return value;
}

float noise1d(float pos)
{
    float d = float(dim);
    float s = 1.0 / d;

    float v0 = pick1d(pos, 0.0 * s);
    float v1 = pick1d(pos, 1.0 * s);

    float t = pos*d - floor(pos*d);
    float tx = f(t);
    float nx = mix(v0, v1, tx);

    return nx;
}

// absolute scaled grad pos in [0;1]
vec2 get_grad_pos(vec2 pos, vec2 grad_direction)
{
    float d = float(dim) - 1.;
    float s = 1.0 / d;
    return floor(pos*d + grad_direction) * s;
}

float grad_dist(vec2 pos, vec2 grad_direction)
{
    float d = float(dim) - 1.;
    float s = 1.0 / d;
    vec2 grad_pos = get_grad_pos(pos, grad_direction);

    // distance to gradient position in [0;1]
    float dist = distance(pos, grad_pos)*d;

    dist *= 2.; // prevent overlap

    return clamp(dist, 0.0, 1.0);
}

float surflets(vec2 pos)
{
    float g00_dist = grad_dist(pos, vec2(0.0, 0.0));
    float g01_dist = grad_dist(pos, vec2(0.0, 1.0));
    float g10_dist = grad_dist(pos, vec2(1.0, 0.0));
    float g11_dist = grad_dist(pos, vec2(1.0, 1.0));

    return ((1. - g00_dist) +
            (1. - g01_dist) +
            (1. - g10_dist) +
            (1. - g11_dist));
}

// symetric version of f()
// t in [-1;1], output in [0;1] (just like f(t))
float sf(float t)
{
    return 1. - f(abs(t));
}

// pos in [0;1]
// grad is a unit vec (length(grad)==1)
float surflet(vec2 pos, vec2 grad)
{
    vec2 xy = pos*2.0 - 1.0; // make each coord in [-1;1]
    float fx = sf(xy.x); // [0;1]
    float fy = sf(xy.y); // [0;1]
    float g = dot(grad, xy);
    float r = fx*fy*g;
    return r/2.0 + .5;
}

float gradients(vec2 pos)
{
    float d = float(dim);
    float s = 1.0 / d;
    vec2 grad = texture2D(tex0_sampler, pos).xy * 2.0 - 1.0; // [0;1] -> [-1;1]
    vec2 spos = fract(pos * d);
    return surflet(spos, grad);
}

#define VALUE_NOISE 0

float pick2d(vec2 pos, vec2 grad_off)
{
    float d = float(dim) - 1.;
    float s = 1.0 / d;

    vec2 pi = floor(pos);
    vec2 tex_pos = fract((pi + grad_off) * s);
#if VALUE_NOISE
    return texture2D(tex0_sampler, tex_pos).x;
#else /* gradient noise */
    vec2 uv = fract(pos) - grad_off;
    vec2 grad = texture2D(tex0_sampler, tex_pos).xy * 2.0 - 1.0;
    return dot(grad, uv);
#endif
}

float noise2d(vec2 pos)
{
    //return gradients(pos);

    //float angle = time * 2.0 * PI;
    //vec2 grad = vec2(cos(angle), sin(angle));
    //return surflet(pos, grad);

    //return surflets(pos);

    float d = float(dim) - 1.;
    float s = 1.0 / d;

    pos *= d;

    vec2 pf = fract(pos);

    float n00 = pick2d(pos, vec2(0.0, 0.0));
    float n01 = pick2d(pos, vec2(0.0, 1.0));
    float n10 = pick2d(pos, vec2(1.0, 0.0));
    float n11 = pick2d(pos, vec2(1.0, 1.0));

    vec2 uv = f(pf);

    float nx0 = mix(n00, n10, uv.x);
    float nx1 = mix(n01, n11, uv.x);
    float nxy = mix(nx0, nx1, uv.y);

#if VALUE_NOISE
    return nxy;
#else
    return nxy + .5; // XXX: why?
#endif
}

#if 0
float pick3d(vec3 pos, vec3 grad_off)
{
    float d = float(dim) - 1.;
    float s = 1.0 / d;

    vec3 pi = floor(pos);
    vec3 tex_pos = fract((pi + grad_off) * s);
    vec3 uv = fract(pos) - grad_off;
    vec3 grad = texture3D(tex0_sampler, tex_pos).xyz * 2.0 - 1.0;
    return dot(grad, uv);
}
#endif

float noise3d(vec3 pos)
{
    float d = float(dim) - 1.;
    float s = 1.0 / d;

    pos *= d;

    vec3 pf = fract(pos);

    return pf.x;
#if 0
    float n000 = pick3d(pos, vec2(0.0, 0.0, 0.0));
    float n100 = pick3d(pos, vec2(1.0, 0.0, 0.0));
    float n010 = pick3d(pos, vec2(0.0, 1.0, 0.0));
    float n110 = pick3d(pos, vec2(1.0, 1.0, 0.0));
    float n001 = pick3d(pos, vec2(0.0, 0.0, 1.0));
    float n101 = pick3d(pos, vec2(1.0, 0.0, 1.0));
    float n011 = pick3d(pos, vec2(0.0, 1.0, 1.0));
    float n111 = pick3d(pos, vec2(1.0, 1.0, 1.0));

    vec2 uvw = f(pf);

    float nx00 = mix(n000, n100, uvw.x);
    float nx01 = mix(n001, n101, uvw.x);
    float nx10 = mix(n010, n110, uvw.x);
    float nx11 = mix(n011, n111, uvw.x);

    float nxy0 = mix(nx00, nx10, uvw.y);
    float nxy1 = mix(nx01, nx11, uvw.y);

    float nxyz = mix(nxy0, nxy1, uvw.z);

    return nxyz;
#endif
}

void main(void)
{
    vec4 color;

    if (profile == 1) { // noise 1d
        float sum = 0.0;
        float max_amp = 0.0;
        float freq = 1.0;
        float amp = 1.0;
        float pos = var_tex0_coord.x/2.0 + time;
        for (int i = 0; i < nb_layers; i++) {
            float nval = noise1d(pos * freq) * amp;
            sum += nval;
            max_amp += amp;
            freq *= lacunarity;
            amp *= gain;
        }
        float n = sum / max_amp;

        float c = step(n, var_tex0_coord.y);
        color = vec4(vec3(c), 1.0);
    } else if (profile == 2) { // noise 2d
        float sum = 0.0;
        float max_amp = 0.0;
        float freq = 1.0;
        float amp = 1.0;
        vec2 pos = var_tex0_coord/2.0 + vec2(time);
        for (int i = 0; i < nb_layers; i++) {
            float nval = noise2d(pos * freq) * amp;
            sum += nval;
            max_amp += amp;
            freq *= lacunarity;
            amp *= gain;
        }
        float n = sum / max_amp;
        color = vec4(vec3(n), 1.0);

    } else if (profile == 3) { // noise 3d
        color = texture2D(tex0_sampler, var_tex0_coord);
    } else if (profile == 4) { // wood
        vec2 pos = var_tex0_coord/2.0 + vec2(time);
        float n = noise2d(pos) * 10.;
        n = n - floor(n);
        color = mix(c1, c2, n);
    } else { // debug
        float n = noise2d(var_tex0_coord);
    }

    gl_FragColor = color;
}
