# =====================
# 参数配置  小区！
# =====================
csv_file = './202404单月基站清洗后交通小区OD矩阵.csv'  # 相对路径：OD矩阵文件
shp_file = './TAZ.shp'  # 相对路径：交通小区shp文件
output_shp = './驿都大道OD.shp'  # 相对路径：输出文件路径
# 括号里输入你想获得的交通小区的编号就可以啦~
target_tazs = {53621, 53622, 53623, 53624, 53625, 53626, 53642, 53641, 53295, 53307, 53611, 53613, 53616, 53617, 53618,
               53619, 53620, 53627, 53298, 53628, 53313, 53607, 53610, 53612, 53310, 53312, 53299, 53374, 53308, 53326,
               53932, 53943, 53944, 53945, 53946, 53947, 53948, 53953, }  # 根据需求填写
# =====================

# 智能编码检测版本 - 自动找到最佳编码
# 结合了诊断工具和主程序的优点

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import os
import glob

print("=" * 60)
print("交通小区OD期望线生成工具 - 智能编码检测版")
print("=" * 60)
print("本版本会自动检测最佳编码，解决读取问题")
print("=" * 60)


# =====================




def print_shapefile_info(gdf, file_path):
    """打印shapefile的详细信息"""
    print(f"\n=== Shapefile 文件信息 ===")
    print(f"文件路径: {file_path}")
    print(f"数据行数: {len(gdf)}")
    print(f"字段列表: {list(gdf.columns)}")
    print(f"几何类型: {gdf.geom_type.unique()}")
    print(f"坐标系: {gdf.crs}")

    if len(gdf.columns) > 1:  # 除了geometry还有其他字段
        print(f"\n前5行数据预览:")
        print(gdf.head())


def find_best_encoding(file_path):
    """
    智能检测最佳编码
    返回: (最佳编码, GeoDataFrame)
    """
    print(f"\n=== 智能编码检测 ===")
    print(f"正在测试不同编码...")

    # 常见编码列表 (按优先级排序)
    encodings = [
        'gbk',  # 中文Windows常用
        'utf-8',  # 跨平台通用
        'gb2312',  # 中文简化版
        'latin1',  # 英文系统
        'cp1252',  # Windows默认
        'gb18030',  # 中文扩展
        'utf-16'  # Unicode
    ]

    best_result = None
    results = []

    for encoding in encodings:
        try:
            print(f"测试编码: {encoding}...", end="")
            gdf = gpd.read_file(file_path, encoding=encoding)

            # 评估结果质量
            field_count = len(gdf.columns)
            results.append({
                'encoding': encoding,
                'success': True,
                'field_count': field_count,
                'gdf': gdf
            })

            status = f"✅ (字段数: {field_count})"
            print(status)

            # 更新最佳结果
            if best_result is None or field_count > best_result['field_count']:
                best_result = results[-1]

        except Exception as e:
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            results.append({
                'encoding': encoding,
                'success': False,
                'error': str(e)
            })
            print(f"❌ ({error_msg})")

    # 分析结果
    print(f"\n=== 编码检测结果 ===")

    if best_result:
        print(f"最佳编码: {best_result['encoding']}")
        print(f"读取结果: {best_result['field_count']} 个字段")
        return best_result['encoding'], best_result['gdf']
    else:
        print(f"❌ 所有编码都失败")

        # 尝试无编码参数
        try:
            print(f"尝试无编码参数读取...")
            gdf = gpd.read_file(file_path)
            print(f"✅ 成功 (使用默认编码)")
            return None, gdf
        except Exception as e:
            print(f"❌ 也失败: {str(e)[:100]}")
            return None, None


# =====================
# 步骤1: 读取OD流量数据 (交通小区矩阵)
# =====================
try:
    print(f"\n=== 步骤1: 读取OD数据 ===")

    # 尝试不同编码读取CSV
    csv_encodings = ['utf-8', 'gbk', 'gb2312']
    df_od = None

    for encoding in csv_encodings:
        try:
            print(f"尝试编码 {encoding} 读取CSV...", end="")
            df_od = pd.read_csv(csv_file, index_col=0, encoding=encoding)
            print(f"✅")
            break
        except:
            print(f"❌", end="")

    if df_od is None:
        raise ValueError("无法读取CSV文件")

    print(f"✅ 成功读取OD数据")
    print(f"   数据形状: {df_od.shape}")
    print(f"   前5行数据:")
    print(df_od.head())

except Exception as e:
    print(f"❌ 读取OD数据时出错: {e}")
    raise

# =====================
# 步骤2: 读取shp文件并获取所有TAZ编号
# =====================
try:
    print(f"\n=== 步骤2: 读取交通小区数据 ===")

    # 首先检查文件是否存在
    if not os.path.exists(shp_file):
        raise FileNotFoundError(f"Shapefile文件不存在: {shp_file}")

    # 检查shapefile完整性
    check_shapefile完整性(shp_file)

    # 智能检测最佳编码
    best_encoding, gdf_zones = find_best_encoding(shp_file)

    if gdf_zones is None:
        # 尝试直接读取dbf文件作为最后的手段
        print(f"\n尝试直接读取dbf文件...")
        dbf_path = os.path.splitext(shp_file)[0] + '.dbf'

        if os.path.exists(dbf_path):
            try:
                from simpledbf import Dbf5

                # 尝试不同编码读取dbf
                dbf_encodings = ['gbk', 'utf-8', 'gb2312']
                df_dbf = None

                for encoding in dbf_encodings:
                    try:
                        print(f"尝试编码 {encoding} 读取dbf...", end="")
                        dbf = Dbf5(dbf_path, codec=encoding)
                        df_dbf = dbf.to_dataframe()
                        print(f"✅")
                        break
                    except:
                        print(f"❌", end="")

                if df_dbf is not None:
                    print(f"✅ 成功读取dbf文件")
                    print(f"   字段数: {len(df_dbf.columns)}")

                    # 读取geometry
                    print(f"读取geometry数据...")
                    gdf_geo = gpd.read_file(shp_file)

                    # 合并数据
                    if len(df_dbf) == len(gdf_geo):
                        gdf_zones = pd.concat([gdf_geo, df_dbf], axis=1)
                        print(f"✅ 成功合并geometry和属性数据")
                    else:
                        raise ValueError(f"数据行数不匹配: geometry={len(gdf_geo)}, 属性={len(df_dbf)}")
                else:
                    raise ValueError("无法读取dbf文件")

            except Exception as e:
                print(f"❌ 直接读取dbf也失败: {e}")
                raise
        else:
            raise FileNotFoundError(f"DBF文件不存在: {dbf_path}")

    # 显示读取结果
    print_shapefile_info(gdf_zones, shp_file)

    # 检查坐标系并转换
    if gdf_zones.crs and gdf_zones.crs.is_geographic:
        print(f"\n转换坐标系至 EPSG:3857")
        gdf_zones = gdf_zones.to_crs(epsg=3857)

except Exception as e:
    print(f"❌ 读取shapefile时出错: {e}")
    raise

# =====================
# 步骤3: 查找和确认TAZ字段
# =====================
taz_field = None
possible_fields = ['TAZ', 'taz', 'Taz', 'TAZ_ID', 'ID', 'id', 'FID', 'INDEX', '编号']

print(f"\n=== 步骤3: TAZ字段识别 ===")

# 如果只有geometry字段，提示用户问题
if len(gdf_zones.columns) == 1 and 'geometry' in gdf_zones.columns:
    print("严重错误: 无法读取到任何属性字段！")
    print("请检查:")
    print("1. Shapefile文件是否完整（特别是.dbf文件）")
    print("2. 文件是否有读取权限")
    print("3. 尝试在ArcGIS或QGIS中打开文件确认是否正常")
    print("4. 考虑重新导出shapefile")
    raise ValueError("无法读取shapefile的属性表信息")

# 首先精确匹配
for field in possible_fields:
    if field in gdf_zones.columns:
        taz_field = field
        print(f"找到精确匹配的TAZ字段: '{taz_field}'")
        break

# 如果没有精确匹配，尝试模糊匹配
if not taz_field:
    print(f"没有找到精确匹配的TAZ字段，尝试模糊匹配...")
    for col in gdf_zones.columns:
        if col != 'geometry':
            col_upper = str(col).upper()
            if any(keyword in col_upper for keyword in ['TAZ', 'ID', 'INDEX', '编号']):
                taz_field = col
                print(f"找到模糊匹配的TAZ字段: '{taz_field}' (包含关键词)")
                break

# 如果仍然没有找到，使用第一个非geometry字段
if not taz_field:
    non_geom_cols = [c for c in gdf_zones.columns if c != 'geometry']
    if non_geom_cols:
        taz_field = non_geom_cols[0]
        print(f"警告: 使用第一个属性字段 '{taz_field}' 作为TAZ字段")
    else:
        print("错误: 没有找到任何非geometry字段")
        raise ValueError("无法找到合适的TAZ字段，请检查shapefile数据")

# 显示所有可用字段供用户确认
print(f"\n所有可用字段:")
for i, col in enumerate(gdf_zones.columns):
    print(f"  {i + 1}. {col}")

print(f"\n当前选择的TAZ字段: '{taz_field}'")

# 让用户有机会手动选择TAZ字段
try:
    user_input = input("\n是否使用此字段作为TAZ标识？(y/n): ").strip().lower()
    if user_input == 'n':
        field_num = int(input(f"请输入TAZ字段的编号 (1-{len(gdf_zones.columns)}): ")) - 1
        if 0 <= field_num < len(gdf_zones.columns):
            taz_field = gdf_zones.columns[field_num]
            print(f"已选择字段: '{taz_field}'")
        else:
            print("无效的编号，使用默认选择")
except KeyboardInterrupt:
    print("\n用户取消操作")
except Exception as e:
    print(f"输入错误: {e}，使用默认选择")

# 验证TAZ字段
if taz_field:
    print(f"\n=== 验证TAZ字段 ===")
    print(f"使用字段 '{taz_field}' 作为TAZ标识")

    try:
        # 查看TAZ字段的数据
        print(f"TAZ字段数据类型: {gdf_zones[taz_field].dtype}")
        print(f"TAZ字段唯一值数量: {gdf_zones[taz_field].nunique()}")

        # 确保TAZ字段是整数类型
        if not pd.api.types.is_integer_dtype(gdf_zones[taz_field]):
            print(f"尝试将TAZ字段转换为整数类型...")
            gdf_zones[taz_field] = pd.to_numeric(gdf_zones[taz_field], errors='coerce').astype('Int64')
            print(f"转换后数据类型: {gdf_zones[taz_field].dtype}")

        # 检查缺失值
        missing_count = gdf_zones[taz_field].isnull().sum()
        if missing_count > 0:
            print(f"警告: TAZ字段中有 {missing_count} 个缺失值")

        # 获取TAZ编号和中心点
        zone_ids = set(gdf_zones[taz_field].dropna().astype(int))
        zone_centroids = gdf_zones.set_index(taz_field).geometry.centroid.to_dict()

        print(f"成功读取 {len(zone_ids)} 个TAZ区域")
        print(f"TAZ编号示例: {list(zone_ids)[:10]}")

    except Exception as e:
        print(f"TAZ字段处理错误: {e}")
        # 提供备选方案 - 使用索引作为TAZ编号
        print("尝试使用索引作为TAZ编号...")
        gdf_zones['TAZ_Index'] = range(1, len(gdf_zones) + 1)
        taz_field = 'TAZ_Index'
        zone_ids = set(gdf_zones[taz_field].astype(int))
        zone_centroids = gdf_zones.set_index(taz_field).geometry.centroid.to_dict()
        print(f"使用索引作为TAZ，共 {len(zone_ids)} 个区域")

else:
    raise ValueError("无法找到合适的TAZ字段，请检查shapefile数据")

# =====================
# 步骤4: 筛选OD数据
# =====================
print(f"\n=== 步骤4: 筛选OD数据 ===")
print(f"目标TAZ数量: {len(target_tazs)}")

# 确保目标TAZ在矩阵的行列中都存在
valid_origins = [taz for taz in target_tazs if taz in df_od.index]
valid_destinations = [taz for taz in target_tazs if taz in df_od.columns]

print(f"有效的起点TAZ数量: {len(valid_origins)}")
print(f"有效的终点TAZ数量: {len(valid_destinations)}")

if valid_origins and valid_destinations:
    print(f"有效的起点TAZ示例: {valid_origins[:10]}")
    print(f"有效的终点TAZ示例: {valid_destinations[:10]}")
else:
    print("警告: 没有找到有效的TAZ，请检查目标TAZ编号是否正确")

# 筛选OD数据，只保留在目标TAZ之间的出行
filtered_od_data = []
for origin in valid_origins:
    for dest in valid_destinations:
        if dest in df_od.columns and origin in df_od.index:
            flow = df_od.loc[origin, dest]
            if flow > 0:  # 只保留有流量的OD对
                filtered_od_data.append({
                    'Origin_TAZ': origin,
                    'Destination_TAZ': dest,
                    'Flow': flow
                })

# 转换为DataFrame
filtered_df = pd.DataFrame(filtered_od_data)
print(f"筛选后的OD数据数量: {len(filtered_df)}")

if len(filtered_df) > 0:
    print(f"OD流量统计:")
    print(f"  最小流量: {filtered_df['Flow'].min()}")
    print(f"  最大流量: {filtered_df['Flow'].max()}")
    print(f"  平均流量: {filtered_df['Flow'].mean():.2f}")
    print(f"  总流量: {filtered_df['Flow'].sum()}")
else:
    print("没有找到符合条件的OD数据")

# =====================
# 步骤5: 构建线要素（LineString）—— 需要空间坐标
# =====================
print(f"\n=== 步骤5: 构建期望线 ===")
lines = []
invalid_count = 0

for _, row in filtered_df.iterrows():
    origin_id = row['Origin_TAZ']
    dest_id = row['Destination_TAZ']
    flow = row['Flow']

    if origin_id not in zone_centroids or dest_id not in zone_centroids:
        invalid_count += 1
        continue

    origin_point = zone_centroids[origin_id]
    dest_point = zone_centroids[dest_id]

    # 检查点是否有效
    if origin_point.is_valid and dest_point.is_valid:
        line_geom = LineString([origin_point, dest_point])
        lines.append({
            'geometry': line_geom,
            'properties': {
                'Origin_TAZ': origin_id,
                'Destination_TAZ': dest_id,
                'Flow': flow,
                'Length': line_geom.length  # 添加线长度
            }
        })
    else:
        invalid_count += 1

print(f"成功创建 {len(lines)} 条期望线")
if invalid_count > 0:
    print(f"无法创建 {invalid_count} 条线（无效的TAZ或几何）")

# =====================
# 步骤6: 创建GeoDataFrame并保存为shp
# =====================
if lines:
    print(f"\n=== 步骤6: 保存结果 ===")
    # 创建GeoDataFrame
    gdf_lines = gpd.GeoDataFrame(
        [line['properties'] for line in lines],
        geometry=[line['geometry'] for line in lines],
        crs=gdf_zones.crs  # 继承原shp的坐标系
    )

    print(f"生成的GeoDataFrame信息:")
    print(f"  数据行数: {len(gdf_lines)}")
    print(f"  字段列表: {list(gdf_lines.columns)}")
    print(f"  坐标系: {gdf_lines.crs}")

    # 确保输出目录存在
    output_dir = os.path.dirname(output_shp)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 保存为shp文件 - 尝试最佳编码
    try:
        save_encodings = ['gbk', 'utf-8'] if best_encoding is None else [best_encoding, 'gbk', 'utf-8']

        for encoding in save_encodings:
            try:
                print(f"尝试使用编码 '{encoding}' 保存...")
                gdf_lines.to_file(output_shp, driver='ESRI Shapefile', encoding=encoding)
                print(f"✅ 成功保存至: {output_shp}")

                # 验证保存的文件
                saved_gdf = gpd.read_file(output_shp, encoding=encoding)
                print(f"✅ 保存验证成功")
                print(f"   保存的记录数: {len(saved_gdf)}")
                break

            except Exception as e:
                print(f"❌ 编码 '{encoding}' 保存失败: {str(e)[:100]}")

    except Exception as e:
        print(f"❌ 所有保存尝试都失败: {e}")
        raise

else:
    print("未找到有效的OD线段，无法生成shp文件。")

print(f"\n" + "=" * 60)
print("处理完成！")
print("=" * 60)
print(f"总步骤总结:")
print(f"1. 读取OD数据: {df_od.shape[0]} x {df_od.shape[1]} 矩阵")
print(f"2. 读取交通小区: {len(gdf_zones)} 个区域")
print(f"3. 筛选目标TAZ: {len(valid_origins)} 个有效起点, {len(valid_destinations)} 个有效终点")
print(f"4. 筛选OD数据: {len(filtered_df)} 条记录")
print(f"5. 生成期望线: {len(lines)} 条")
if lines:
    print(f"6. 输出文件: {output_shp}")

