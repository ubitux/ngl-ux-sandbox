uniform sampler1D tex0_sampler;
varying float var_tex0_coord;

float pick1d(float pos, float off)
{
    float value_point = fract(pos + off);
    float value = texture1D(tex0_sampler, value_point).x;
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

void main(void)
{
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
    vec4 color = vec4(vec3(c), 1.0);

    gl_FragColor = color;
}
