uniform sampler3D tex0_sampler;
varying vec2 var_tex0_coord;
uniform vec3 tex0_dimensions;

#if 1
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

#if 0
    return pf.x;
#else
    float n000 = pick3d(pos, vec3(0.0, 0.0, 0.0));
    float n100 = pick3d(pos, vec3(1.0, 0.0, 0.0));
    float n010 = pick3d(pos, vec3(0.0, 1.0, 0.0));
    float n110 = pick3d(pos, vec3(1.0, 1.0, 0.0));
    float n001 = pick3d(pos, vec3(0.0, 0.0, 1.0));
    float n101 = pick3d(pos, vec3(1.0, 0.0, 1.0));
    float n011 = pick3d(pos, vec3(0.0, 1.0, 1.0));
    float n111 = pick3d(pos, vec3(1.0, 1.0, 1.0));

    vec3 uvw = f(pf);

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
    float sum = 0.0;
    float max_amp = 0.0;
    float freq = 1.0;
    float amp = 1.0;
    vec3 pos = vec3(var_tex0_coord, time);
    for (int i = 0; i < nb_layers; i++) {
        float nval = noise3d(pos * freq) * amp;
        sum += nval;
        max_amp += amp;
        freq *= lacunarity;
        amp *= gain;
    }
    float n = sum / max_amp;
    vec4 color = vec4(vec3(n), 1.0);

    gl_FragColor = color;
}
