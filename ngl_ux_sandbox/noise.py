import array
import math
import random
from OpenGL import GL

from pynodegl import (
        AnimKeyFrameBuffer,
        AnimKeyFrameFloat,
        AnimatedBufferVec2,
        AnimatedFloat,
        BufferFloat,
        BufferVec2,
        BufferVec3,
        Geometry,
        Program,
        Quad,
        Render,
        Rotate,
        Texture2D,
        Texture3D,
        UniformFloat,
        UniformVec4,
        UniformInt,
)

from pynodegl_utils.misc import scene

from utils import get_myfrag, get_myvert


@scene(ndim={'type': 'range', 'range': [1,8]},
       nb_layers={'type': 'range', 'range': [1,8]},
       lacunarity={'type': 'range', 'range': [0.01, 10], 'unit_base': 100},
       gain={'type': 'range', 'range': [0.01, 10], 'unit_base': 100})
def noise1d(cfg, ndim=4, nb_layers=6, lacunarity=2.0, gain=0.5):
    random.seed(0)
    random_dim = 1<<ndim

    shader_header = '#version 100\nprecision highp float;\n'

    def get_rand():
        return array.array('f', [random.uniform(0, 1) for x in range(random_dim)])

    random_buf = BufferFloat(data=get_rand())
    random_tex = Texture2D(data_src=random_buf, width=random_dim, height=1)

    quad = Quad((-1, -1, 0), (2, 0, 0), (0, 2, 0))
    prog = Program(fragment=shader_header
                           + get_myfrag('noise-common')
                           + get_myfrag('noise1d'),
                   vertex=shader_header
                         + get_myvert('noise'))

    utime_animkf = [AnimKeyFrameFloat(0, 0),
                    AnimKeyFrameFloat(cfg.duration, 1)]
    utime = UniformFloat(anim=AnimatedFloat(utime_animkf))

    render = Render(quad, prog)
    render.update_textures(tex0=random_tex)
    render.update_uniforms(dim=UniformInt(random_dim))
    render.update_uniforms(nb_layers=UniformInt(nb_layers))
    render.update_uniforms(time=utime)
    #render.update_uniforms(profile=UniformInt(1))
    render.update_uniforms(lacunarity=UniformFloat(lacunarity))
    render.update_uniforms(gain=UniformFloat(gain))

    return render


@scene(ndim={'type': 'range', 'range': [0,8]})
def segment_debug(cfg, ndim=2):
    dim = 1 << ndim

    random.seed(0)

    # generate NxN RGB colors
    colors = [random.random() for x in range(dim**2 * 3)]
    c_data = array.array('f', colors)
    c_buf = BufferVec3(data=c_data)
    c_tex = Texture2D(data_src=c_buf, width=dim, height=dim)

    #quad = Quad((-1, 1, 0), (2, 0, 0), (0, -2, 0)) # origin in bottom left
    quad = Quad((-1, -1, 0), (2, 0, 0), (0, 2, 0))
    prog = Program(fragment=get_myfrag('segment'))
    render = Render(quad, prog)
    render.update_textures(tex0=c_tex)
    render.update_uniforms(dim=UniformInt(dim))
    return render


def _permuted_2d_gradients(n, pad=0, r=1.0):
    step = 2. * math.pi / float(n)
    angles = [i*step for i in range(n)]
    random.shuffle(angles)
    grad = []
    for angle in angles:
        xy = [math.cos(angle)*r, math.sin(angle)*r]
        xy = [(x + 1.0) / 2.0 for x in xy] # prevent opengl from clipping automatically during picking
        grad += xy
        grad += [0] * pad
    return grad

@scene(ndim={'type': 'range', 'range': [0,8]},
       nb_layers={'type': 'range', 'range': [1,8]},
       lacunarity={'type': 'range', 'range': [0.01, 10], 'unit_base': 100},
       gain={'type': 'range', 'range': [0.01, 10], 'unit_base': 100})
def noise2d(cfg, ndim=4, nb_layers=6, lacunarity=2.0, gain=0.5):
    random.seed(0)
    random_dim = (1<<ndim) + 1

    shader_header = '#version 100\nprecision highp float;\n'

    nb_gradients = random_dim**2
    #print 'nb_gradients', nb_gradients
    #print 'dim', random_dim

    random_vals = _permuted_2d_gradients(nb_gradients)

    random_data = array.array('f', random_vals)
    random_buf = BufferVec2(data=random_data)
    random_tex = Texture2D(data_src=random_buf, width=random_dim, height=random_dim)

    quad = Quad((-1, 1, 0), (2, 0, 0), (0, -2, 0))
    prog = Program(fragment=shader_header
                           + get_myfrag('noise-common')
                           + get_myfrag('noise2d'))

    utime_animkf = [AnimKeyFrameFloat(0, 0),
                    AnimKeyFrameFloat(cfg.duration, 1)]
    utime = UniformFloat(anim=AnimatedFloat(utime_animkf))

    render = Render(quad, prog)
    render.update_textures(tex0=random_tex)
    render.update_uniforms(dim=UniformInt(random_dim))
    render.update_uniforms(nb_layers=UniformInt(nb_layers))
    render.update_uniforms(time=utime)
    render.update_uniforms(profile=UniformInt(0))
    render.update_uniforms(lacunarity=UniformFloat(lacunarity))
    render.update_uniforms(gain=UniformFloat(gain))

    return render

@scene(ndim={'type': 'range', 'range': [0,8]},
       c1={'type': 'color'}, c2={'type': 'color'},
       lacunarity={'type': 'range', 'range': [0.01, 10], 'unit_base': 100},
       gain={'type': 'range', 'range': [0.01, 10], 'unit_base': 100})
def wood(cfg, ndim=4,
         c1=(0.23, 0.17, 0.08, 1.0), c2=(0.47, 0.38, 0.27, 1.0),
         lacunarity=2.0, gain=0.5):

    random.seed(0)
    random_dim = (1<<ndim) + 1

    shader_header = '#version 100\nprecision highp float;\n'

    nb_gradients = random_dim**2

    random_vals = _permuted_2d_gradients(nb_gradients)

    random_data = array.array('f', random_vals)
    random_buf = BufferVec2(data=random_data)
    random_tex = Texture2D(data_src=random_buf, width=random_dim, height=random_dim)

    quad = Quad((-1, 1, 0), (2, 0, 0), (0, -2, 0))
    prog = Program(fragment=shader_header
                           + get_myfrag('noise-common')
                           + get_myfrag('noise2d'))

    utime_animkf = [AnimKeyFrameFloat(0, 0),
                    AnimKeyFrameFloat(cfg.duration, 1)]
    utime = UniformFloat(anim=AnimatedFloat(utime_animkf))

    render = Render(quad, prog)
    render.update_textures(tex0=random_tex)
    render.update_uniforms(dim=UniformInt(random_dim))
    render.update_uniforms(nb_layers=UniformInt(1))
    render.update_uniforms(time=utime)
    render.update_uniforms(profile=UniformInt(1))
    render.update_uniforms(lacunarity=UniformFloat(lacunarity))
    render.update_uniforms(gain=UniformFloat(gain))
    render.update_uniforms(c1=UniformVec4(c1))
    render.update_uniforms(c2=UniformVec4(c2))

    return render


# uniform distribution of vectors of unit length 1
def _get_rand(nb, nb_comp=2, pad=0):
    r = []
    for i in range(nb):
        vec = [random.gauss(0, 1) for x in range(nb_comp)]
        #vec = [random.uniform(-1, 1) for x in range(nb_comp)]
        vec += [0] * pad
        mag = math.sqrt(sum(x*x for x in vec))
        r += [x/mag for x in vec]
    return r


@scene(ndim={'type': 'range', 'range': [1,8]},
       nb_layers={'type': 'range', 'range': [1,8]},
       lacunarity={'type': 'range', 'range': [0.01, 10], 'unit_base': 100},
       gain={'type': 'range', 'range': [0.01, 10], 'unit_base': 100})
def noise3d(cfg, ndim=4, nb_layers=1, lacunarity=2.0, gain=0.5):
    random.seed(0)
    random_dim = (1<<ndim) + 1

    #shader_header = '#version 100\nprecision highp float;\n'
    shader_header = '#version 130\n' if cfg.glbackend != 'gles' else '#version 310 es\n'

    nb_gradients = random_dim**2

    grad_set = (
        ( 0, 1, 1), ( 0, 1,-1),
        ( 0,-1, 1), ( 0,-1,-1),
        ( 1, 0, 1), ( 1, 0,-1),
        (-1, 0, 1), (-1, 0,-1),
        ( 1, 1, 0), ( 1,-1, 0),
        (-1, 1, 0), (-1,-1, 0),
    )

    def get_rand():
        #return array.array('f', _get_rand(random_dim**2, nb_comp=3))
        r = []
        for i in range(nb_gradients):
            r += random.choice(grad_set)
        return array.array('f', r)

    random_buffer = BufferVec3(data=get_rand())
    random_tex = Texture2D(data_src=random_buffer, width=random_dim, height=random_dim)

    quad = Quad((-1, -1, 0), (2, 0, 0), (0, 2, 0))
    prog = Program(fragment=shader_header
                           + get_myfrag('noise-common')
                           + get_myfrag('noise3d'),
                   vertex=shader_header
                         + get_myvert('noise3d'))

    utime_animkf = [AnimKeyFrameFloat(0, 0),
                    AnimKeyFrameFloat(cfg.duration/2.0, 1),
                    AnimKeyFrameFloat(cfg.duration, 0)]
    utime = UniformFloat(anim=AnimatedFloat(utime_animkf))

    render = Render(quad, prog)
    render.update_textures(tex0=random_tex)
    render.update_uniforms(dim=UniformInt(random_dim))
    render.update_uniforms(nb_layers=UniformInt(nb_layers))
    render.update_uniforms(time=utime)
    render.update_uniforms(lacunarity=UniformFloat(lacunarity))
    render.update_uniforms(gain=UniformFloat(gain))

    return render
