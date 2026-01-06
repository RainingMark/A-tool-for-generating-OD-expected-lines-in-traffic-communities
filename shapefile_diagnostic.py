"""
Shapefile诊断工具
用于检测和解决shapefile读取问题
"""

import geopandas as gpd
import os
import glob
import pandas as pd
from simpledbf import Dbf5


def diagnose_shapefile(file_path):
    """
    诊断shapefile文件读取问题

    Args:
        file_path: shapefile路径 (.shp)
    """

    print("=" * 60)
    print("Shapefile 诊断工具")
    print("=" * 60)

    # 基本文件检查
    print("\n1. 基本文件检查")
    print("-" * 30)

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return

    print(f"✅ 文件存在: {file_path}")

    # 检查shapefile完整性
    base_path = os.path.splitext(file_path)[0]
    required_files = {
        '.shp': '主文件',
        '.shx': '索引文件',
        '.dbf': '属性表文件',
        '.prj': '投影文件'
    }

    file_status = {}
    for ext, desc in required_files.items():
        file_exists = os.path.exists(base_path + ext)
        file_status[ext] = file_exists
        status = "✅" if file_exists else "❌"
        print(f"{status} {base_path}{ext} - {desc}")

    # 检查文件权限
    print(f"\n2. 文件权限检查")
    print("-" * 30)
    try:
        with open(file_path, 'rb') as f:
            f.read(10)
        print("✅ 读取权限正常")
    except PermissionError:
        print("❌ 没有读取权限")
        return

    # 尝试读取shapefile
    print(f"\n3. 读取测试")
    print("-" * 30)

    # 尝试不同编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1', 'cp1252']
    read_results = []

    for encoding in encodings:
        try:
            print(f"\n尝试编码: {encoding}")
            gdf = gpd.read_file(file_path, encoding=encoding)
            print(f"✅ 成功读取")
            print(f"   数据行数: {len(gdf)}")
            print(f"   字段列表: {list(gdf.columns)}")
            print(f"   几何类型: {gdf.geom_type.unique()}")
            print(f"   坐标系: {gdf.crs}")

            if len(gdf.columns) > 1:
                print(f"   数据预览:")
                print(gdf.head(3))

            read_results.append({
                'encoding': encoding,
                'success': True,
                'gdf': gdf,
                'fields': len(gdf.columns)
            })

        except Exception as e:
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            print(f"❌ 失败: {error_msg}")
            read_results.append({
                'encoding': encoding,
                'success': False,
                'error': str(e)
            })

    # 分析结果
    print(f"\n4. 结果分析")
    print("-" * 30)

    successful_reads = [r for r in read_results if r['success']]

    if successful_reads:
        best_result = max(successful_reads, key=lambda x: x['fields'])
        print(f"最佳结果: 编码 '{best_result['encoding']}'")
        print(f"   字段数: {best_result['fields']}")

        if best_result['fields'] == 1 and 'geometry' in best_result['gdf'].columns:
            print("⚠️  警告: 只读取到geometry字段，没有属性表")

            # 尝试直接读取dbf
            if file_status['.dbf']:
                print(f"\n5. 尝试直接读取DBF文件")
                print("-" * 30)
                try:
                    dbf = Dbf5(base_path + '.dbf')
                    df_dbf = dbf.to_dataframe()
                    print(f"✅ 成功读取DBF文件")
                    print(f"   字段数: {len(df_dbf.columns)}")
                    print(f"   字段列表: {list(df_dbf.columns)}")
                    print(f"   数据预览:")
                    print(df_dbf.head(3))

                    # 检查是否可以合并
                    gdf_geo = best_result['gdf']
                    if len(df_dbf) == len(gdf_geo):
                        print(f"\n✅ 可以合并geometry和属性表")
                        gdf_complete = pd.concat([gdf_geo, df_dbf], axis=1)
                        print(f"   合并后字段: {list(gdf_complete.columns)}")
                        print(f"   数据预览:")
                        print(gdf_complete.head(3))

                        # 保存修复后的文件
                        output_path = base_path + '_fixed.shp'
                        gdf_complete.to_file(output_path, driver='ESRI Shapefile', encoding='utf-8')
                        print(f"\n✅ 修复后的文件已保存至: {output_path}")

                except Exception as e:
                    print(f"❌ 读取DBF失败: {e}")
            else:
                print("❌ DBF文件缺失，无法读取属性表")

        else:
            print("✅ 读取正常，包含属性表")

    else:
        print("❌ 所有编码尝试都失败")

        # 尝试不带编码读取
        try:
            print(f"\n尝试不带编码参数读取")
            gdf = gpd.read_file(file_path)
            print(f"✅ 成功读取 (不带编码)")
            print(f"   数据行数: {len(gdf)}")
            print(f"   字段列表: {list(gdf.columns)}")
        except Exception as e:
            print(f"❌ 失败: {e}")

    # 检查文件大小
    print(f"\n5. 文件大小分析")
    print("-" * 30)
    for ext, desc in required_files.items():
        if os.path.exists(base_path + ext):
            size = os.path.getsize(base_path + ext)
            print(f"{base_path}{ext}: {size:,} 字节")

    # 版本信息
    print(f"\n6. 环境信息")
    print("-" * 30)
    print(f"GeoPandas版本: {gpd.__version__}")
    print(f"GDAL版本: {gpd.io.file.fiona.drvsupport.gdal_version}")
    print(f"Fiona版本: {gpd.io.file.fiona.__version__}")

    print(f"\n诊断完成！")
    print("=" * 60)


def batch_check_folder(folder_path):
    """
    批量检查文件夹中的shapefile
    """
    print(f"批量检查文件夹: {folder_path}")
    print("=" * 60)

    shp_files = glob.glob(os.path.join(folder_path, "*.shp"))

    if not shp_files:
        print("未找到shapefile文件")
        return

    for shp_file in shp_files:
        print(f"\n处理: {os.path.basename(shp_file)}")
        diagnose_shapefile(shp_file)
        print("\n" + "=" * 40 + "\n")


# 使用示例
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            batch_check_folder(path)
        elif os.path.isfile(path) and path.lower().endswith('.shp'):
            diagnose_shapefile(path)
        else:
            print("请提供有效的shapefile路径或文件夹")
    else:
        print("使用方法:")
        print("1. 检查单个文件: python shapefile_diagnostic.py path/to/file.shp")
        print("2. 批量检查文件夹: python shapefile_diagnostic.py path/to/folder")
