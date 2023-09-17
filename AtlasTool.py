# 图集拆分合并工具
# Author: lujiahao
# Date: 2023年9月17日15:59:57

import argparse
import sys
import json
from pathlib import Path

from PIL import Image


def run(p_source, p_out):
    pass


def split_egret(p_json, p_png, p_out):
    # 打开png文件
    img = Image.open(p_png)

    # 打开json文件
    path_json = Path(p_json)
    out_name = path_json.stem  # 文件名
    if not path_json.exists():
        sys.exit(f'[ERROR]文件不存在：{str(path_json)}')
    obj_json = json.loads(path_json.read_text(encoding='utf-8'))

    # print(obj_json['mc'])
    # print(obj_json['res'])
    res_dict = obj_json['res']
    for k, v in res_dict.items():
        # print(k, v)
        x = int(v['x'])
        y = int(v['y'])
        w = int(v['w'])
        h = int(v['h'])
        # print(x, y, w, h)

        # 从大图中裁剪出小图
        single_png = img.crop((x, y, x + w, y + h))

        out_path = Path(p_out).joinpath(out_name).joinpath(k)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        single_png.save(out_path)

    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--input', type=str, default='', help='输入文件路径')
    parser.add_argument('--output', type=str, default='', help='输出文件路径')
    args = parser.parse_args()

    app = sys.argv[0]

    json_url = 'testres/role_10008.json'
    png_url = 'testres/role_10008.png'
    out_url = 'testout'

    split_egret(json_url, png_url, out_url)
