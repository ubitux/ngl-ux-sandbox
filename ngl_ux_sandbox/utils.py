import os
from math import cos, sin, sqrt

def get_myshader(filename):
    shader_path = os.path.join(os.path.dirname(__file__), 'shaders')
    return open(os.path.join(shader_path, filename)).read()

def get_myfrag(name):
    return get_myshader(name + '.frag')

vec_sub = lambda v1, v2: [a - b for a, b in zip(v1, v2)]
vec_add = lambda v1, v2: [a + b for a, b in zip(v1, v2)]
vec_mul = lambda v1, v2: [a * b for a, b in zip(v1, v2)]

def vec3_cross(v1, v2):
    return [v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0]]

vec_len = lambda v: sqrt(sum(x*x for x in v))

def vec_norm(v):
    if tuple(v) == (0,0,0):
        return v
    f = 1. / vec_len(v);
    return [x*f for x in v]

vec3_normal = lambda v1, v2: vec_norm(vec3_cross(v1, v2))

mat3xvec3 = lambda m, v: [
    m[0]*v[0] + m[3]*v[1] + m[6]*v[2],
    m[1]*v[0] + m[4]*v[1] + m[7]*v[2],
    m[2]*v[0] + m[5]*v[1] + m[8]*v[2],
]

def vec3_rot(v, rot):
    x, y, z = rot
    rotx = [1., 0., 0., 0., cos(x), sin(x), 0., -sin(x), cos(x)]
    roty = [cos(y), 0., -sin(y), 0., 1., 0., sin(y), 0., cos(y)]
    rotz = [cos(z), sin(z), 0., -sin(z), cos(z), 0., 0., 0., 1.]
    v = mat3xvec3(rotx, v)
    v = mat3xvec3(roty, v)
    v = mat3xvec3(rotz, v)
    return v
