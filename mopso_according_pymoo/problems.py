"""
该文件为存放问题的文件
"""

import numpy as np
from pymoo.core.problem import ElementwiseProblem
from pyswmm import Simulation, Nodes, Subcatchments, LidControls, LidGroup, LidUnit
from swmm.toolkit.shared_enum import SystemAttribute
from pyswmm import Output
from datetime import datetime, timedelta
from pymoo.util.misc import stack


class MyProblem(ElementwiseProblem):

    def __init__(self, x_num, obj_num, constr_num, x_min, x_max,
                 sub_lid_price, name_list, inp_path, out_path, lid_kid_list):
        """
        初始化问题类的一些参数
        :param x_num: 自变量的数量
        :param obj_num: 目标函数的数量
        :param constr_num: 限制条件的数量
        :param x_min: 自变量的最小值（np数组）
        :param x_max: 自变量的最大值（np数组）
        :param sub_lid_price: lid的面积的单价(元/平方米)
        :param name_list: 存放汇水分区的名称
        :param inp_path: inp文件的地址，用于启动仿真
        :param out_path: out文件的地址，用于查看系统径流量的结果
        :param lid_kid_list: 存放lid种类的列表
        """
        super().__init__(n_var=x_num,
                         n_obj=obj_num,
                         n_constr=constr_num,
                         xl=x_min,
                         xu=x_max)
        self.sub_lid_price = sub_lid_price
        self.name_list = name_list
        self.inp_path = inp_path
        self.out_path = out_path
        self.lid_kid_list = lid_kid_list

    def _evaluate(self, x, out, *args, **kwargs):
        """
        进行函数计算与约束条件判断的类函数
        :param x: 自变量的集合，list类型
        :param out: 输出值
        :param args:
        :param kwargs:
        :return: 改变out字典中输出值和约束条件的值
        """

        """
        f1,f2,f3分别为三个需要优化的函数
        """
        """
        f1:LID的面积之和最小的函数
        """
        f1 = np.sum(x)
        """
        f2:价格之和最小的函数
        """
        price_sum = 0
        # 通过name_list和surface，计算LID控制器的总价值
        for i in range(len(self.name_list)):
            for name in self.sub_lid_price:
                price_sum += float(self.sub_lid_price[name]) * x[i]
        f2 = price_sum
        """
        f3:系统径流量最小的函数
        """
        # runoff_former:未加LID之前的径流量最大值
        runoff_former = 76.61833190917969
        # 径流量的列表
        runoff = []
        with Simulation(self.inp_path) as sim:
            for i in range(len(self.name_list)):
                # 取出每一个集水区中lid
                lid = LidUnit(sim._model, self.name_list[i], 0)
                # 改动lid面积
                lid.unit_area = x[i]
            # 开始仿真
            sim.start()
            # 仿真时间间隔为600秒
            sim.step_advance(60)
            # 仿真依赖这一步执行
            for step in sim:
                pass
        with Output(self.out_path) as out:
            ts = out.system_series(SystemAttribute.RUNOFF_FLOW, datetime(2022, 6, 28, 1), datetime(2022, 6, 28, 6))
            for index in ts:
                runoff.append(ts[index])
            print(max(runoff))
            f3 = (max(runoff) / runoff_former) * 100

        """
        g1:规定的约束条件，即最小体积
        """
        # g1为规定的约束
        volume_wish = 156322.82  # 体积的最小期望值
        # 读取inp文件中的lid的深度值
        lid_deep = []
        with Simulation(self.inp_path) as sim:
            print("")
            for lid_kid in self.lid_kid_list:
                rain_barrel = LidControls(sim)[lid_kid]
                lid_deep.append(rain_barrel.surface.thickness * 0.01)
        # volume_all: LID体积的总值
        volume_all = 0
        # 计算此种情况下LID的体积总值
        for i in range(len(x)):
            volume_all += x[i] * lid_deep[i]

        # g1 < 0
        g1 = volume_wish - volume_all

        # out["F"] = np.column_stack([f1, f2, f3])
        out["F"] = [f1, f2, f3]
        out["G"] = [g1]