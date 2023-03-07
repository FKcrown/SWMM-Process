# 导入pyswmm包
from pyswmm import Simulation, Nodes, Links

# 定义inp文件的路径
inp_file = "example.inp"

# 定义输出csv文件的路径
out_file = "output.csv"

# 定义超参数
rainfall = 10 # 降雨量（英寸）
duration = 3600 # 模拟时长（秒）
interval = 300 # 输出时间间隔（秒）

# 创建Simulation对象，打开inp文件
sim = Simulation(inp_file)

# 设置降雨量
sim.rainfall("RainGage1").setPattern([rainfall])

# 创建Nodes对象，获取所有节点的名称
nodes = Nodes(sim)
node_names = nodes._nodeid()

# 创建Links对象，获取所有连接的名称
links = Links(sim)
link_names = links._linkid()

# 打开输出csv文件，并写入表头
with open(out_file, "w") as f:
    f.write("Time")
    for name in node_names:
        f.write("," + name + "_depth") # 节点深度（英尺）
    for name in link_names:
        f.write("," + name + "_flow") # 连接流量（立方英尺/秒）
    f.write("\n")

    # 开始模拟循环
    for step in sim:
        # 获取当前模拟时间（秒）
        time = sim.current_time - sim.start_time
        time = time.total_seconds()

        # 如果当前时间是输出时间间隔的倍数，则写入输出数据
        if time % interval == 0:
            f.write(str(time))
            for node in nodes:
                f.write("," + str(node.depth))
            for link in links:
                f.write("," + str(link.flow))
            f.write("\n")

        # 如果当前时间超过模拟时长，则结束循环
        if time >= duration:
            break

    # 关闭Simulation对象，释放资源
    sim.close()