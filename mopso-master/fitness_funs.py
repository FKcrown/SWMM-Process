# encoding: utf-8
import numpy as np
from pyswmm import Simulation, Nodes, Subcatchments, LidControls, LidGroup, LidUnit
from swmm.toolkit.shared_enum import SystemAttribute
from pyswmm import Output
from datetime import datetime, timedelta

from sklearn.preprocessing import MinMaxScaler

# def normalize(x):
#     """
#     对三个数进行MinMaxScaler归一化
#     """
#     scaler = MinMaxScaler()
#     norm_x = scaler.fit_transform(np.array(x).reshape(-1,1))
#     return list(norm_x.flatten())


def normalize(x):
    """
    对三个数进行对数归一化
    """
    log_x = np.log10(x) / np.log10(100)
    min_log_x = np.min(log_x)
    norm_log_x = log_x - min_log_x
    return norm_log_x / np.sum(norm_log_x)






def fitness_(in_, inp_path, out_path, name_list, subcatchment_lid_price):
    """
    该函数用于计算优化值的适应度
    :param in_:待优化的例子的n维坐标（每一维代表着每一个LID的面积）
    :param inp_path:inp文件的地址
    :param out_path:out文件的地址
    :param name_list:存放分区的名称
    :param subcatchment_lid_price:存放name_list中分区对应LID控制器的单价
    :return:三个函数分别的适应度
    """
    # runoff_former: 未加LID之前的S-29径流量最大值
    runoff_former = 76.61833190917969

    """
    LID总面积最小的函数:fit_1
    """
    # 面积最小的函数:fit_1
    fit_1 = np.sum(in_)

    """
    价格最小的函数:fit_2
    """
    # 计算LID控制器的总价值
    # name_list = name_list  # 存放分区的名称，例如：S-1
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
    # 径流量的列表
    runoff = []
    # 径流量衰减最大的函数:fit_3
    with Simulation(inp_path) as sim:
        for i in range(len(name_list)):
            # 取出每一个集水区中lid
            lid = LidUnit(sim._model, name_list[i], 0)
            # 改动lid面积
            lid.unit_area = in_[i]
        # 开始仿真
        sim.start()
        # 仿真时间间隔为600秒
        sim.step_advance(60)
        # 仿真依赖这一步执行
        for step in sim:
            pass

    with Output(out_path) as out:
        ts = out.system_series(SystemAttribute.RUNOFF_FLOW, datetime(2022, 6, 28, 1), datetime(2022, 6, 28, 6))
        for index in ts:
            runoff.append(ts[index])
        print(max(runoff))
        fit_3 = (max(runoff) / runoff_former) * 100
        # fit_3 = max(runoff)

    # print([fit_1, fit_2, fit_3])
    # fit_1 = np.log10(fit_1) / np.log10(100)
    # fit_2 = np.log10(fit_2) / np.log10(1000)
    # fit_3 *= 0.1
    # print([fit_1, fit_2, fit_3])
    # re_list = normalize([fit_1, fit_2, fit_3])
    # print(re_list)

    return [fit_1, fit_2, fit_3]
