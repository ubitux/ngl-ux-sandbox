#version 100

precision mediump float;
varying vec3 var_normal;
uniform vec3 color;

void main(void)
{
    gl_FragColor = clamp(vec4(color + var_normal, 1.0), 0.0, 1.0);
}
