import array
import math
import random
from OpenGL import GL

from pynodegl import (
        AnimKeyFrameFloat,
        AnimatedFloat,
        BufferVec3,
        Geometry,
        Program,
        Quad,
        Render,
        Rotate,
        UniformVec4,
)

from pynodegl_utils.misc import scene, get_shader

@scene(n={'type': 'range', 'range': [1,100000]},
       gauss={'type': 'bool'})
def sphere(cfg, n=4000, gauss=True):
    random.seed(0)

    cfg.duration = 15.

    quad = Quad((-1, -1, 0), (2, 0, 0), (0, 2, 0))
    prog = Program(fragment=get_shader('color'))

    scale = 1.3
    r = []
    for i in range(n):
        if gauss:
            vec = [random.gauss(0, 1) for x in range(3)]
        else:
            vec = [random.uniform(-1, 1) for x in range(3)]
        mag = math.sqrt(sum(x*x for x in vec)) * scale
        r += [x/mag for x in vec]

    vertices_data = array.array('f', r)
    vertices_buf = BufferVec3(data=vertices_data)
    geom = Geometry(vertices_buf)
    geom.set_draw_mode(GL.GL_POINTS)

    render = Render(geom, prog)
    render.update_uniforms(color=UniformVec4(value=(1,1,1,1)))

    for i in range(3):
        rot_animkf = AnimatedFloat([AnimKeyFrameFloat(0, 0),
                                    AnimKeyFrameFloat(cfg.duration, 360 * (i + 1))])
        axis = [int(i == x) for x in range(3)]
        render = Rotate(render, axis=axis, anim=rot_animkf)

    return render
