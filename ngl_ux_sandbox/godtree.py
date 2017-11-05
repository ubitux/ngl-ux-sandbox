import array
from math import sin, cos, pi, pow

import random
from OpenGL import GL

from pynodegl_utils.misc import scene
from pynodegl import (
        AnimKeyFrameBuffer,
        AnimKeyFrameFloat,
        AnimKeyFrameVec3,
        AnimatedBufferVec3,
        AnimatedFloat,
        AnimatedVec3,
        Camera,
        GLState,
        Geometry,
        Group,
        Program,
        Render,
        Rotate,
        Translate,
        UniformFloat,
        UniformVec3,
        UniformVec4,
)

from utils import (
        get_frag,
        vec_add,
        vec3_rot,
        vec3_normal,
)

class _Branch:

    def __init__(self, min_h, max_h):
        self.children = {}
        self.coords = []
        self.final_height = random.uniform(min_h, max_h)

    def new_child(self, variance, branch):
        var1, var2 = -variance/2., variance/2.
        angle_x = random.uniform(var1, var2) * pi/180.
        angle_z = random.uniform(var1, var2) * pi/180.
        self.children[(angle_x, angle_z)] = branch


def _get_tree_specs(nb_generations, variance_split, variance_cont,
                    proba_split, proba_cont, min_h, max_h):

    def _get_branch_specs(generations_left):
        branch = _Branch(min_h, max_h)
        if generations_left > 1:
            if random.random() < proba_split:
                branch.new_child(variance_split, _get_branch_specs(generations_left - 1))
                branch.new_child(variance_split, _get_branch_specs(generations_left - 1))
            if random.random() < proba_cont:
                branch.new_child(variance_cont, _get_branch_specs(generations_left - 1))
        return branch

    root = _Branch(min_h, max_h)
    root.new_child(variance_cont, _get_branch_specs(nb_generations))
    return root


def _get_target_coord(orig, h, angles, twist, init=[0, 0, 0]):
    coord = vec_add(init, [0, h, 0])
    angle_x, angle_z = angles
    rot_vec = [angle_x, twist, angle_z]
    coord = vec3_rot(coord, rot_vec)
    coord = vec_add(coord, orig)
    return coord


def _get_circle(r, h, angles, twist=0, orig=(0,0,0), k=8):
    vertices = []
    step = 2. * pi / k
    for i in range(k):
        angle = i * step
        coord = [sin(angle)*r, 0, cos(angle)*r]
        coord = _get_target_coord(orig, h, angles, twist=twist, init=coord)
        vertices.append(coord)
    return vertices


_exp_helper = lambda x, exp_base: (pow(exp_base, x) - 1.0) / (exp_base - 1.0)
_exp_in  = lambda x, exp_base=128.0:       _exp_helper(      x, exp_base);
_exp_out = lambda x, exp_base=128.0: 1.0 - _exp_helper(1.0 - x, exp_base);


def _add_tree_coords(branch, t, birth_step, max_w, twist,
                     angles=[0, 0], skel_coords=[0, 0, 0], level=0):
    branch_age = max(min(t - level*birth_step, 1.0), 0)
    h = branch_age * branch.final_height if level else 0
    w = _exp_in(branch_age) * max_w if branch.children else 0
    tw = branch_age * twist if level else 0
    vertices = _get_circle(r=w, h=h, angles=angles, orig=skel_coords)
    branch.coords.append(vertices)
    for child_angles, child_branch in branch.children.items():
        child_angles = vec_add(angles, child_angles)
        child_skel_coords = _get_target_coord(skel_coords, h, child_angles, tw)
        _add_tree_coords(child_branch, t, birth_step, max_w, twist,
                         child_angles, child_skel_coords, level + 1)


@scene(variance_split={'type': 'range', 'range': [0, 180]},
       variance_cont={'type': 'range', 'range': [0, 90]},
       birth_step={'type': 'range', 'range': [0.01, 1], 'unit_base': 100},
       max_w={'type': 'range', 'range': [0.01, 1], 'unit_base': 100},
       min_h={'type': 'range', 'range': [0.01, 1], 'unit_base': 100},
       max_h={'type': 'range', 'range': [0.01, 1], 'unit_base': 100},
       twist={'type': 'range', 'range': [0, 45]},
       proba_split={'type': 'range', 'range': [0, 1], 'unit_base': 100},
       proba_cont={'type': 'range', 'range': [0, 1], 'unit_base': 100},
       seed={'type': 'range', 'range': [0, 1000]},
       debug_color={'type': 'bool'},
       green={'type': 'color'},
       brown={'type': 'color'})
def godtree(cfg, variance_split=35, variance_cont=5,
            birth_step=0.1, max_w=0.15, min_h=0.15, max_h=0.45, twist=0,
            proba_split=0.5, proba_cont=0.9,
            seed=0, debug_color=False,
            green=(0.29, 0.46, 0.29, 1.0), brown=(0.22, 0.21, 0.21, 1.0)):

    random.seed(seed)

    assert birth_step > 0 and birth_step <= 1
    nb_generations = int(1. / birth_step) # one new generation every birth step
    tree_specs = _get_tree_specs(nb_generations, variance_split, variance_cont,
                                 proba_split, proba_cont, min_h, max_h)
    for t in range(nb_generations + 1):
        _add_tree_coords(tree_specs, t/float(nb_generations),
                         birth_step, max_w, twist*pi/2.)

    if debug_color:
        fragment = get_frag('godtree-dbgcolor')
    else:
        ugreen = UniformVec4(green)
        ubrown = UniformVec4(brown)
        fragment = get_frag('godtree')

    program = Program(fragment=fragment)

    grow_time = cfg.duration / 2.0 # grow only during half the demo time

    def _get_renders(branch, level=0):

        renders = []
        for _, child_branch in branch.children.items():

            # Branch vertices and normals
            vertices_animkf = []
            normals_animkf  = []
            for i, coords in enumerate(zip(branch.coords, child_branch.coords)):

                time = i * grow_time / float(nb_generations)

                vertices_data = array.array('f')
                normals_data = array.array('f')
                bottom_coords, top_coords = coords
                bottom_top_coords = zip(bottom_coords, top_coords)
                prev = bottom_top_coords[-1]
                for bottom1, top1 in bottom_top_coords:
                    bottom0, top0 = prev
                    prev = bottom1, top1
                    norm = vec3_normal(top0, bottom1)
                    normals_data.extend(norm * 6)
                    vertices_data.extend(bottom0 + bottom1 + top0 +
                                         bottom1 + top0    + top1)
                vertices_animkf.append(AnimKeyFrameBuffer(time, vertices_data))
                normals_animkf.append(AnimKeyFrameBuffer(time, normals_data))

            vertices = AnimatedBufferVec3(vertices_animkf)
            normals  = AnimatedBufferVec3(normals_animkf)
            shape = Geometry(vertices, normals=normals,
                             draw_mode=GL.GL_TRIANGLES)
            render = Render(shape, program)

            # Colors
            if debug_color:
                ucolor = UniformVec3([random.uniform(0.5, 1) for i in range(3)])
                render.update_uniforms(color=ucolor)
            else:
                render.update_uniforms(green=ugreen, brown=ubrown)

            # Age
            time_birth = level * birth_step
            time_old   = time_birth + 1.0
            age_animkf = [AnimKeyFrameFloat(time_birth * grow_time, 0),
                          AnimKeyFrameFloat(time_old   * grow_time, 1)]
            uage = UniformFloat(anim=AnimatedFloat(age_animkf))
            render.update_uniforms(age=uage)

            renders.append(render)
            renders += _get_renders(child_branch, level + 1)

        return renders

    renders = _get_renders(tree_specs)

    node = Group(children=renders)
    node.add_glstates(GLState(GL.GL_DEPTH_TEST, GL.GL_TRUE))
    rot_animkf = [AnimKeyFrameFloat(0, 0),
                  AnimKeyFrameFloat(cfg.duration, 360*2)]
    node = Rotate(node, axis=(0,1,0), anim=AnimatedFloat(rot_animkf))
    node = Translate(node, (0, -1, 0))
    camera = Camera(node)
    return camera
