#version 100

#define PI 3.14159265358979323846

precision mediump float;
varying vec2 var_tex0_coord;
uniform sampler2D tex0_sampler;
uniform int dim;

void main(void)
{
    vec2 p = var_tex0_coord;
    float f2 = (sqrt(3.0)-1.0)*0.5;
    float s = (p.x + p.y) * f2;

    vec2 tp = fract(p + s);


    vec3 color = texture2D(tex0_sampler, tp).rgb;
    //vec3 color = vec3(tp.x, 0.0, 0.0);
    gl_FragColor = vec4(color, 1.0);
}
