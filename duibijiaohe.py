"""
对比测试脚本 - 找出为什么诊断工具可以读取而主程序不能
"""

import geopandas as gpd
import pandas as pd
import os
import sys
from simpledbf import Dbf5


def compare_reading_methods(shp_path):
    """
    对比不同的读取方法
    """
    print("=" * 80)
    print("Shapefile 读取方法对比测试")
    print("=" * 80)

    if not os.path.exists(shp_path):
        print(f"❌ 文件不存在: {shp_path}")
        return

    base_path = os.path.splitext(shp_path)[0]

    # 方法1: 诊断工具的读取方式
    print(f"\n【方法1】诊断工具的读取方式 (多种编码尝试)")
    print("-" * 60)

    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1', 'cp1252']
    best_result = None

    for encoding in encodings:
        try:
            print(f"尝试编码: {encoding}")
            gdf = gpd.read_file(shp_path, encoding=encoding)
            print(f"✅ 成功读取")
            print(f"   字段数: {len(gdf.columns)}")
            print(f"   字段列表: {list(gdf.columns)}")

            if best_result is None or len(gdf.columns) > best_result['fields']:
                best_result = {
                    'encoding': encoding,
                    'gdf': gdf,
                    'fields': len(gdf.columns)
                }

        except Exception as e:
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            print(f"❌ 失败: {error_msg}")

    if best_result:
        print(f"\n最佳结果: 使用编码 '{best_result['encoding']}'")
        diag_gdf = best_result['gdf']
    else:
        print(f"\n❌ 所有编码都失败")
        diag_gdf = None

    # 方法2: 主程序的读取方式 (GBK优先)
    print(f"\n【方法2】主程序的读取方式 (GBK优先)")
    print("-" * 60)

    main_gdf = None
    main_error = None

    try:
        print(f"尝试GBK编码...")
        main_gdf = gpd.read_file(shp_path, encoding='gbk')
        print(f"✅ 成功读取")
        print(f"   字段数: {len(main_gdf.columns)}")
        print(f"   字段列表: {list(main_gdf.columns)}")

    except Exception as e:
        main_error = str(e)
        print(f"❌ GBK编码失败: {main_error[:150]}")

        # 尝试直接读取dbf
        try:
            dbf_path = base_path + '.dbf'
            if os.path.exists(dbf_path):
                print(f"\n尝试直接读取dbf文件...")
                dbf = Dbf5(dbf_path, codec='gbk')
                df_dbf = dbf.to_dataframe()
                print(f"✅ 成功读取dbf")

                # 读取geometry
                gdf_geo = gpd.read_file(shp_path)

                # 合并
                if len(df_dbf) == len(gdf_geo):
                    main_gdf = pd.concat([gdf_geo, df_dbf], axis=1)
                    print(f"✅ 成功合并数据")
                    print(f"   字段数: {len(main_gdf.columns)}")

        except Exception as e2:
            print(f"❌ 直接读取dbf也失败: {str(e2)[:100]}")

    # 方法3: 直接使用诊断工具找到的最佳编码
    print(f"\n【方法3】使用诊断工具找到的最佳编码")
    print("-" * 60)

    if best_result:
        try:
            print(f"使用编码 '{best_result['encoding']}'...")
            optimized_gdf = gpd.read_file(shp_path, encoding=best_result['encoding'])
            print(f"✅ 成功读取")
            print(f"   字段数: {len(optimized_gdf.columns)}")
            print(f"   字段列表: {list(optimized_gdf.columns)}")

        except Exception as e:
            print(f"❌ 失败: {str(e)[:100]}")

    # 对比结果
    print(f"\n【对比结果】")
    print("-" * 60)

    if diag_gdf is not None and main_gdf is not None:
        print(f"诊断工具: {len(diag_gdf.columns)} 个字段")
        print(f"主程序: {len(main_gdf.columns)} 个字段")

        if len(diag_gdf.columns) > len(main_gdf.columns):
            print(f"⚠️  发现差异: 诊断工具读取到更多字段")
            print(f"   可能原因: 主程序使用的编码不是最佳选择")
            print(f"   建议: 使用 '{best_result['encoding']}' 编码替代GBK")

    elif diag_gdf is not None and main_gdf is None:
        print(f"❌ 主程序完全失败，但诊断工具成功")
        print(f"   成功编码: '{best_result['encoding']}'")
        print(f"   主程序错误: {main_error}")

    elif diag_gdf is None and main_gdf is not None:
        print(f"✅ 主程序成功，诊断工具失败 (不常见)")

    else:
        print(f"❌ 所有方法都失败")

    # 提供修复建议
    print(f"\n【修复建议】")
    print("-" * 60)

    if best_result:
        print(f"1. 修改主程序，使用最佳编码 '{best_result['encoding']}':")
        print(f"   在 od_analysis_gbk.py 中:")
        print(f"   将 'encoding='gbk'' 改为 'encoding='{best_result['encoding']}''")
        print(f"   大约在第85行:")
        print(f"   gdf_zones = gpd.read_file(shp_file, encoding='{best_result['encoding']}')")

        print(f"\n2. 或者使用自动编码检测版本:")
        print(f"   python od_analysis_fixed.py")

        print(f"\n3. 或者创建自定义版本:")
        print(f"   根据测试结果，您的文件最佳编码是: {best_result['encoding']}")

    # 生成修复后的代码
    if best_result and best_result['encoding'] != 'gbk':
        print(f"\n【修复后的代码片段】")
        print("-" * 60)

        fix_code = f"""
# 修复后的读取代码 - 使用最佳编码 '{best_result['encoding']}'
print(f"使用最佳编码 '{best_result['encoding']}' 读取shapefile...")
try:
    gdf_zones = gpd.read_file(shp_file, encoding='{best_result['encoding']}')
    print(f"✅ 成功使用 '{best_result['encoding']}' 编码读取")
except Exception as e:
    print(f"❌ '{best_result['encoding']}' 编码失败: {{e}}")
    # 回退到其他方法...
"""
        print(fix_code)


def test_specific_file(shp_path):
    """测试特定文件"""
    print(f"测试文件: {shp_path}")
    print("=" * 60)

    # 检查文件基本信息
    if os.path.exists(shp_path):
        print(f"文件大小: {os.path.getsize(shp_path)} 字节")

        # 检查相关文件
        base_path = os.path.splitext(shp_path)[0]
        related_files = ['.shp', '.shx', '.dbf', '.prj']
        for ext in related_files:
            file_path = base_path + ext
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  {ext}: {size} 字节")
            else:
                print(f"  {ext}: 缺失")

    # 运行对比测试
    compare_reading_methods(shp_path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        shp_path = sys.argv[1]
        test_specific_file(shp_path)
    else:
        print("使用方法:")
        print("python compare_reading.py path/to/your/file.shp")
        print("\n这个工具会对比不同的读取方法，找出最佳解决方案")
