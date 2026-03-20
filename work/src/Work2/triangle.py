import taichi as ti
import math
import numpy as np

ti.init(arch=ti.cpu)

res = (700, 700)



# 三角形顶点
vertices = [
    ti.Vector([2.0, 0.0, -2.0, 1.0]),
    ti.Vector([0.0, 2.0, -2.0, 1.0]),
    ti.Vector([-2.0, 0.0, -2.0, 1.0])
]

# 接收一个旋转角度（角度制），返回绕 Z 轴旋转该角度的模型变换矩阵
def get_model_matrix(angle):
    angle = angle * math.pi / 180.0 #把旋转角度转换为弧度制

    cos = math.cos(angle)
    sin = math.sin(angle)

    model = ti.Matrix([
        [cos, -sin, 0, 0],
        [sin, cos,  0, 0],
        [0,   0,    1, 0],
        [0,   0,    0, 1]
    ])

    return model


# 接收相机位置（三维向量），返回视图变换矩阵。需要将相机平移至世界坐标系的原点
def get_view_matrix(eye_pos):

    view = ti.Matrix([
        [1, 0, 0, -eye_pos[0]],
        [0, 1, 0, -eye_pos[1]],
        [0, 0, 1, -eye_pos[2]],
        [0, 0, 0, 1]
    ])

    return view


# 接收视场角（Y 轴方向，角度制）、屏幕长宽比、近截面距离和远截面距离，返回透视投影矩阵
def get_projection_matrix(eye_fov, aspect_ratio, zNear, zFar):

    fov = eye_fov * math.pi / 180.0

    n = -zNear
    f = -zFar

    #计算边界
    t = math.tan(fov / 2) * abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r

    # 透视到正交变换
    persp_to_ortho = ti.Matrix([
        [n, 0, 0, 0],
        [0, n, 0, 0],
        [0, 0, n + f, -n * f],
        [0, 0, 1, 0]
    ])

    # 正交投影
    ortho_scale = ti.Matrix([
        [2/(r-l), 0, 0, 0],
        [0, 2/(t-b), 0, 0],
        [0, 0, 2/(n-f), 0],
        [0, 0, 0, 1]
    ])

    ortho_translate = ti.Matrix([
        [1, 0, 0, -(r+l)/2],
        [0, 1, 0, -(t+b)/2],
        [0, 0, 1, -(n+f)/2],
        [0, 0, 0, 1]
    ])

    ortho = ortho_scale @ ortho_translate

    projection = ortho @ persp_to_ortho

    return projection

#定义初始参数
eye_pos = ti.Vector([0.0, 0.0, 5.0])

eye_fov = 45
aspect_ratio = 1
zNear = 0.1
zFar = 50

angle = 0

gui = ti.GUI("MVP Triangle", res)


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
    projection = get_projection_matrix(eye_fov, aspect_ratio, zNear, zFar)

    MVP = projection @ view @ model

    screen_pos = []

    for v in vertices:
        p = MVP @ v

        # 透视除法
        p = p / p[3]

        x = (p[0] + 1) * 0.5
        y = (p[1] + 1) * 0.5

        screen_pos.append(np.array([x, y], dtype=float))

    gui.clear(0x112F41)

    gui.line(begin=screen_pos[0], end=screen_pos[1], radius=2, color=0xFF0000)
    gui.line(begin=screen_pos[1], end=screen_pos[2], radius=2, color=0x00FF00)
    gui.line(begin=screen_pos[2], end=screen_pos[0], radius=2, color=0x0000FF)

    gui.show()