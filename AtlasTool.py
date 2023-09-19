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


def find_frames(p_obj_json):
    if 'mc' in p_obj_json:
        for k in p_obj_json['mc']:
            child = p_obj_json['mc'][k]
            if 'frames' in child:
                return child['frames']
    return None


def split_egret(p_json, p_png, p_out, p_offset_type=0):
    """
    拆分egret图集
    :param p_json: json路径
    :param p_png: png路径
    :param p_out: 输出路径
    :param p_offset_type: 偏移值类型 0:左上角 1:中心点
    :return:
    """
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
    # 遍历找到”frames“字段
    frames = find_frames(obj_json)
    if frames is None:
        sys.exit(f'[ERROR]没有找到frames字段')

    vo_dict = {}
    frame_index = 0

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

    if p_offset_type == 0:
        handle_lett_top(vo_dict, img_big, p_out, out_name)
    elif p_offset_type == 1:
        handle_center(vo_dict, img_big, p_out, out_name)


def handle_lett_top(p_vo_dict: dict, p_img_big: Image, p_out, p_out_name):
    """
    处理偏移类型为左上角的类型
    :param p_vo_dict:
    :param p_img_big:
    :param p_out:
    :param p_out_name:
    :return:
    """
    max_w = 0  # 记录最大宽度
    max_h = 0  # 记录最大高度

    min_cut_left = 0  # 记录最小裁剪左边距
    min_cut_top = 0  # 记录最小裁剪上边距

    vo_list = p_vo_dict.values()
    print(vo_list)
    for vo in vo_list:
        # 计算新图像的宽高
        new_w = 0
        new_h = 0
        cut_left = 0
        cut_top = 0

        if vo.offx < 0:
            new_w = vo.w - vo.offx
            cut_left = -vo.offx
        else:
            new_w = max(vo.w, vo.offx)
        if vo.offy < 0:
            new_h = vo.h - vo.offy
            cut_top = -vo.offy
        else:
            new_h = max(vo.h, vo.offy)

        if new_w > max_w:
            max_w = new_w
        if new_h > max_h:
            max_h = new_h

        if cut_left > 0:
            if min_cut_left == 0:
                min_cut_left = cut_left
            else:
                if cut_left < min_cut_left:
                    min_cut_left = cut_left
        if cut_top > 0:
            if min_cut_top == 0:
                min_cut_top = cut_top
            else:
                if cut_top < min_cut_top:
                    min_cut_top = cut_top

    print(f'[INFO]最大宽度：{max_w}')
    print(f'[INFO]最大高度：{max_h}')
    print(f'[INFO]最小裁剪左边距：{min_cut_left}')
    print(f'[INFO]最小裁剪上边距：{min_cut_top}')

    for vo in vo_list:
        single_png = p_img_big.crop((vo.x, vo.y, vo.x + vo.w, vo.y + vo.h))

        new_img = Image.new('RGBA', (max_w, max_h), (0, 0, 0, 0))

        # 将单张图贴到新图像中
        new_img.paste(single_png, (-vo.offx, -vo.offy))

        # 裁剪
        new_img = new_img.crop((min_cut_left, min_cut_top, max_w, max_h))

        png_name = vo.name
        if png_name.endswith('.png'):
            png_name = png_name[:-4]
        out_path = Path(p_out).joinpath(p_out_name).joinpath(png_name + '.png')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        new_img.save(out_path)
        print(f'[INFO]保存成功：{str(out_path)}')


def handle_center(p_vo_dict: dict[str, VoFrame], p_img_big: Image, p_out, p_out_name):
    """
    处理偏移类型为中心点的类型
    :param p_vo_dict:
    :param p_img_big:
    :param p_out:
    :param p_out_name:
    :return:
    """
    max_left = 0
    max_top = 0
    max_right = 0
    max_bottom = 0

    vo_list = p_vo_dict.values()
    for vo in vo_list:
        left = -vo.offx
        top = -vo.offy
        right = vo.w - left
        bottom = vo.h - top

        if left > max_left:
            max_left = left
        if top > max_top:
            max_top = top
        if right > max_right:
            max_right = right
        if bottom > max_bottom:
            max_bottom = bottom

    max_w = max_left + max_right
    max_h = max_top + max_bottom

    for vo in vo_list:
        single_png = p_img_big.crop((vo.x, vo.y, vo.x + vo.w, vo.y + vo.h))
        new_img = Image.new('RGBA', (max_w, max_h), (0, 0, 0, 0))

        paste_x = max_left + vo.offx
        paste_y = max_top + vo.offy

        new_img.paste(single_png, (paste_x, paste_y))

        png_name = vo.name
        if png_name.endswith('.png'):
            png_name = png_name[:-4]
        out_path = Path(p_out).joinpath(p_out_name).joinpath(png_name + '.png')
        out_path.parent.mkdir(parents=True, exist_ok=True)
        new_img.save(out_path)
        print(f'[INFO]保存成功：{str(out_path)}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--input', type=str, default='', help='输入文件路径')
    parser.add_argument('--output', type=str, default='', help='输出文件路径')
    args = parser.parse_args()

    app = sys.argv[0]

    json_url = 'testres/role_10008.json'
    png_url = 'testres/role_10008.png'
    out_url = 'testout'
    offset_type = 0

    split_egret(json_url, png_url, out_url, offset_type)
