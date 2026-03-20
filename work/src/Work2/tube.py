import taichi as ti
import math
import numpy as np

ti.init(arch=ti.cpu)

res = (700, 700)

# 立方体顶点
cube_vertices = [
    ti.Vector([-1.0,-1.0,-1.0,1.0]),
    ti.Vector([ 1.0,-1.0,-1.0,1.0]),
    ti.Vector([ 1.0, 1.0,-1.0,1.0]),
    ti.Vector([-1.0, 1.0,-1.0,1.0]),

    ti.Vector([-1.0,-1.0, 1.0,1.0]),
    ti.Vector([ 1.0,-1.0, 1.0,1.0]),
    ti.Vector([ 1.0, 1.0, 1.0,1.0]),
    ti.Vector([-1.0, 1.0, 1.0,1.0])
]

# 12条边
cube_edges = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7)
]

# Model Matrix（双轴旋转）
def get_model_matrix(angle):

    rad = angle * math.pi / 180

    cos = math.cos(rad)
    sin = math.sin(rad)

    # Y轴旋转
    rot_y = ti.Matrix([
        [cos,0,sin,0],
        [0,1,0,0],
        [-sin,0,cos,0],
        [0,0,0,1]
    ])

    # X轴旋转
    rot_x = ti.Matrix([
        [1,0,0,0],
        [0,cos,-sin,0],
        [0,sin,cos,0],
        [0,0,0,1]
    ])

    return rot_y @ rot_x


# 视图矩阵函数
def get_view_matrix(eye_pos):

    return ti.Matrix([
        [1,0,0,-eye_pos[0]],
        [0,1,0,-eye_pos[1]],
        [0,0,1,-eye_pos[2]],
        [0,0,0,1]
    ])


# 投影矩阵函数
def get_projection_matrix(fov, aspect, zNear, zFar):

    fov = fov * math.pi / 180

    n = -zNear
    f = -zFar

    t = math.tan(fov/2)*abs(n)
    b = -t
    r = aspect*t
    l = -r

    persp_to_ortho = ti.Matrix([
        [n,0,0,0],
        [0,n,0,0],
        [0,0,n+f,-n*f],
        [0,0,1,0]
    ])

    ortho_scale = ti.Matrix([
        [2/(r-l),0,0,0],
        [0,2/(t-b),0,0],
        [0,0,2/(n-f),0],
        [0,0,0,1]
    ])

    ortho_translate = ti.Matrix([
        [1,0,0,-(r+l)/2],
        [0,1,0,-(t+b)/2],
        [0,0,1,-(n+f)/2],
        [0,0,0,1]
    ])

    return ortho_scale @ ortho_translate @ persp_to_ortho


# 顶点变换函数
def transform_vertices(MVP):

    screen_pos = []

    for v in cube_vertices:

        p = MVP @ v

        # 透视除法
        p = p / p[3]

        # NDC → 屏幕
        x = (p[0]+1)*0.5
        y = (p[1]+1)*0.5

        screen_pos.append(np.array([x,y],dtype=float))

    return screen_pos


# 初始化参数
eye_pos = ti.Vector([0.0,0.0,5.0])

eye_fov = 45
aspect_ratio = 1
zNear = 0.1
zFar = 50

angle = 0

gui = ti.GUI("3D MVP Cube", res)


while gui.running:

    for e in gui.get_events():

        if e.key == ti.GUI.ESCAPE:
            gui.running = False

        if e.key == 'a':
            angle += 5

        if e.key == 'd':
            angle -= 5


    model = get_model_matrix(angle)
    view = get_view_matrix(eye_pos)
    projection = get_projection_matrix(
        eye_fov, aspect_ratio, zNear, zFar
    )

    MVP = projection @ view @ model

    screen_pos = transform_vertices(MVP)

    gui.clear(0x112F41)


    # 底面
    for i in range(4):
        e = cube_edges[i]
        gui.line(screen_pos[e[0]],screen_pos[e[1]],radius=2,color=0xFF5555)

    # 顶面
    for i in range(4,8):
        e = cube_edges[i]
        gui.line(screen_pos[e[0]],screen_pos[e[1]],radius=2,color=0x55FF55)

    # 竖边
    for i in range(8,12):
        e = cube_edges[i]
        gui.line(screen_pos[e[0]],screen_pos[e[1]],radius=2,color=0x5599FF)


    gui.show()