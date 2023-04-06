# encoding: utf-8
import numpy as np
from pyswmm import Simulation, Nodes, Subcatchments, LidControls, LidGroup, LidUnit


def fitness_(in_, inp_path, name_list, subcatchment_lid_price):
    runoff_former = 0.4
    # 面积最小的函数:fit_1
    # fit_1 = 0

    # 价格最小的函数:fit_2
    fit_2 = 0
    # 计算LID控制器的总价值
    name_list = name_list  # 存放分区的名称，例如：S-1
    surface = in_  # 存放name_list中分区对应LID控制器的面积，单位：平方米
    # 存放name_list中分区对应LID控制器的单价，单位：元/平方米
    dict1 = subcatchment_lid_price
    sum = 0
    # 通过name_list和surface，计算LID控制器的总价值
    for i in range(len(name_list)):
        for name in dict1:
            sum = sum + float(dict1[name]) * surface[i]
    fit_2 = sum

    """
    调用inp文件
    """
    # 径流量衰减最大的函数:fit_3
    fit_3 = 0
    with Simulation(inp_path) as sim:
        for i in range(len(name_list)):
            # 取出每一个集水区中lid
            lid = LidUnit(sim._model, name_list[i], 0)
            # 改动lid面积
            lid.unit_area = in_[i]

        subcatch_object = Subcatchments(sim)
        # 径流量的检测值
        sc = subcatch_object["S-29"]
        # 开始仿真
        sim.start()
        # 仿真时间间隔为600秒
        sim.step_advance(600)
        # 径流量的列表
        runoff = []
        for step in sim:
            # 看该汇水分区的径流量
            # print(sc.runoff)
            runoff.append(sc.runoff)
        # print("finish")
        print(max(runoff))
        fit_3 = max(runoff)

    return [fit_2, fit_3]
