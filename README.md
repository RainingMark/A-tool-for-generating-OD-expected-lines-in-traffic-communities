# 交通小区OD期望线生成工具

## 项目概述

这是一个用于生成交通小区OD（Origin-Destination）期望线的Python工具。它可以根据给定的OD矩阵数据和交通小区空间数据，生成可视化的期望线，帮助交通规划人员分析交通流分布。

## 功能特点

- 智能编码检测：自动识别和处理不同编码的数据文件
- 灵活的参数配置：支持自定义目标交通小区和输出路径
- 完整的错误处理：提供详细的错误信息和诊断功能
- 可视化输出：生成标准的Shapefile格式期望线文件
- 兼容性强：支持多种编码和格式的数据文件

## 依赖环境

- Python 3.7+
- pandas>=1.3.0,<2.0.0
- geopandas>=0.9.0,<1.0.0
- shapely>=1.7.0,<2.0.0
- simpledbf>=0.2.6
- fiona>=1.8.0
- pyproj>=3.0.0
- rtree>=0.9.7

## 安装步骤

1. 克隆或下载项目代码
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 准备数据文件：
   - OD矩阵CSV文件：包含交通小区之间的出行流量数据
   - 交通小区Shapefile文件：包含交通小区的空间信息

2. 配置参数：
   在`交通小区局部OD绘制.py`文件中配置以下参数：
   ```python
   # OD矩阵文件路径
   csv_file = './OD矩阵示例模板.csv'
   # 交通小区Shapefile文件路径
   shp_file = './TAZ.shp'
   # 输出期望线文件路径
   output_shp = './期望线输出.shp'
   # 目标交通小区集合
   target_tazs = {53621, 53622, 53623, 53624}
   ```

3. 运行程序：
   ```bash
   python 交通小区局部OD绘制.py
   ```

4. 查看结果：
   - 程序会生成一个Shapefile文件，包含期望线的几何信息和属性数据
   - 可以使用ArcGIS、QGIS等GIS软件打开查看

## 项目结构

```
├── 交通小区局部OD绘制.py  # 主程序文件
├── duibijiaohe.py        # 对比测试工具
├── shapefile_diagnostic.py  # Shapefile诊断工具
├── requirements.txt      # 依赖包列表
├── .gitignore            # Git忽略文件
├── OD矩阵示例模板.csv     # OD矩阵示例数据
├── 目标交通小区配置示例.xlsx  # 目标交通小区配置示例
├── 示例数据说明.md        # 示例数据说明文档
└── README.md             # 项目说明文档
```

## 示例数据

项目提供了以下示例数据：

1. `OD矩阵示例模板.csv`：包含4个交通小区之间的出行流量示例
2. `目标交通小区配置示例.xlsx`：包含交通小区配置示例
3. `示例数据说明.md`：详细说明数据格式和准备方法

## 注意事项

1. 数据文件编码：
   - 程序会自动检测文件编码，但建议使用UTF-8或GBK编码

2. 交通小区字段：
   - 程序会自动识别TAZ字段（支持TAZ、taz、ID、编号等字段名）
   - 如果自动识别失败，程序会提示用户手动选择

3. 坐标系：
   - 建议使用投影坐标系（如EPSG:3857）以获得准确的距离计算
   - 程序会自动检测和转换坐标系

4. 输出文件：
   - 输出的Shapefile文件包含Origin_TAZ、Destination_TAZ、Flow和Length字段
   - 可以使用GIS软件进行进一步的分析和可视化

## 故障排除

如果遇到问题，可以使用以下工具进行诊断：

1. `shapefile_diagnostic.py`：用于诊断Shapefile文件读取问题
   ```bash
   python shapefile_diagnostic.py path/to/your/file.shp
   ```

2. `duibijiaohe.py`：用于对比不同的读取方法
   ```bash
   python duibijiaohe.py path/to/your/file.shp
   ```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：your-email@example.com
- GitHub：https://github.com/your-username/your-repository
