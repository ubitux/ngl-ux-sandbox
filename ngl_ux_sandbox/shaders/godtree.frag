#version 100

precision mediump float;
varying vec3 var_normal;
uniform vec4 green;
uniform vec4 brown;
uniform float age;

void main(void)
{
    vec4 light_color = vec4(1.0);
    vec4 material_color = mix(green, brown, age);
    vec3 light = vec3(1.0);
    float cosTheta = clamp(dot(var_normal, light), 0.0, 1.0) * 2.0;
    gl_FragColor = material_color * light_color * cosTheta + vec4(0.1, 0.1, 0.1, 0.0);
}
