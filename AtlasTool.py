# 图集拆分合并工具
# Author: lujiahao
# Date: 2023年9月17日15:59:57

import argparse
import sys
import json
from pathlib import Path

from PIL import Image


class VoFrame:
    name: str = ''
    offx: int = 0
    offy: int = 0
    # 帧序号 从1开始
    frame_index: int = 0
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0


def run(p_source, p_out):
    pass


def split_egret(p_json, p_png, p_out):
    # 打开png文件
    img_big = Image.open(p_png)

    # 打开json文件
    path_json = Path(p_json)
    out_name = path_json.stem  # 文件名
    if not path_json.exists():
        sys.exit(f'[ERROR]文件不存在：{str(path_json)}')
    obj_json = json.loads(path_json.read_text(encoding='utf-8'))

    # print(obj_json['mc'])
    # print(obj_json['res'])
    res_dict = obj_json['res']
    frames = obj_json['mc']['mc']['frames']
    vo_dict = {}
    frame_index = 0

    max_w = 0  # 记录最大宽度
    max_h = 0  # 记录最大高度

    for data in frames:
        frame_index += 1
        vo = VoFrame()
        vo.name = data['res']
        vo.offx = data['x']
        vo.offy = data['y']
        vo.frame_index = frame_index

        vo.x = res_dict[vo.name]['x']
        vo.y = res_dict[vo.name]['y']
        vo.w = res_dict[vo.name]['w']
        vo.h = res_dict[vo.name]['h']

        vo_dict[vo.name] = vo

        # 计算新图像的宽高
        new_w = 0
        if vo.offx < 0:
            new_w = vo.w - vo.offx
        else:
            new_w = max(vo.w, vo.offx)
        new_h = 0
        if vo.offy < 0:
            new_h = vo.h - vo.offy
        else:
            new_h = max(vo.h, vo.offy)

        if new_w > max_w:
            max_w = new_w
        if new_h > max_h:
            max_h = new_h

    for vo in vo_dict.values():
        single_png = img_big.crop((vo.x, vo.y, vo.x + vo.w, vo.y + vo.h))

        new_img = Image.new('RGBA', (max_w, max_h), (0, 0, 0, 0))

        # 将单张图贴到新图像中
        new_img.paste(single_png, (-vo.offx, -vo.offy))
        out_path = Path(p_out).joinpath(out_name).joinpath(vo.name)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        new_img.save(out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--input', type=str, default='', help='输入文件路径')
    parser.add_argument('--output', type=str, default='', help='输出文件路径')
    args = parser.parse_args()

    app = sys.argv[0]

    json_url = 'testres/1.json'
    png_url = 'testres/1.png'
    out_url = 'testout'

    split_egret(json_url, png_url, out_url)
