"""
此文件专用于inp文件的读写学习与测试
"""
import pyswmm
from tqdm import tqdm
import pandas as pd
from pyswmm import Simulation, Nodes, Subcatchments


# inp_file:用于存放inp文件的地址
inp_flie = r'D:\PythonProject\Image_recognition\SWMM\1121-2D.inp'

# 打开一个inp文件
with Simulation(inp_flie) as sim:
    subcatchments = Subcatchments(sim)
    print(len(subcatchments))
    S1 = subcatchments['SJ9999']
    print(S1.area)
    # 更改汇水分区中管道的面积
    S1.area = 50
    print(S1.area)
    # # 读取每一个集水区
    for subcatchment in tqdm(Subcatchments(sim)):
    # for subcatchment in Subcatchments(sim):
        # 打印每一个集水区的子集水区
        print(subcatchment.subcatchmentid)


