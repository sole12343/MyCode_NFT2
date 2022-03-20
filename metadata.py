#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import time
import os
import json
from copy import deepcopy
from tqdm import tqdm, trange
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

'''
    主要功能：
           输入系列NFT的名字，生成所有图片每一个NFT的json文件，需要修改item名字和ipfs的URL
           会pandas读取csv文件，然后找到每个NFT的所有标签属性、名字(系列名字+“#num”)、描述、图片路径
           这些信息生成json文件后，全部都会上传到区块链，无法修改。           
    函数：
        generate_paths ： 根据文件名 获取元数据和 JSON 文件 的保存路径
        clean_attributes ： 返回json文件所需要的对应的标签属性
        get_attribute_metadata ： 获取属性元数据的函数,zfill_count是告诉zfill函数总共数字是几位的，需要补几个0，
                                    最后统一格式比如3位：001，010，100。。。。
'''



# Base metadata. MUST BE EDITED.
# BASE_IMAGE_URL 只需要一个ipfs pinata 的文件夹链接，就可以生成全部的图片链接了
BASE_IMAGE_URL = "ipfs://QmQogs7apTkdr7QzniEDE3vNrhh5fEz9vBhXX2C2XF6PwY"
BASE_NAME = "IT_Ape #"

BASE_JSON = {
    "name": BASE_NAME,
    "description": "IT_Ape is a new 10,000 unique IT Ape NFTs - unique digital collectibles living on the Ethereum blockchain.Your IT Ape serves as your social identity and allows you to participate in club activities and enjoy exclusive member benefits .",
    "image": BASE_IMAGE_URL,
    "attributes": [],
}


# Get metadata and JSON files path based on edition
# 根据文件名 获取元数据和 JSON 文件路径
def generate_paths(edition_name):
    edition_path = os.path.join('output', 'edition ' + str(edition_name))
    metadata_path = os.path.join(edition_path, 'metadata.csv')
    json_path = os.path.join(edition_path, 'json')

    return edition_path, metadata_path, json_path

# Function to convert snake case to sentence case
def clean_attributes(attr_name):
    
    clean_name = attr_name.replace('_', ' ')
    clean_name = list(clean_name)
    
    for idx, ltr in enumerate(clean_name):
        if (idx == 0) or (idx > 0 and clean_name[idx - 1] == ' '):
            # upper() 方法将字符串中的小写字母转为大写字母。
            clean_name[idx] = clean_name[idx].upper()
    
    clean_name = ''.join(clean_name)
    return clean_name


# Function to get attribure metadata
# 获取属性元数据的函数,zfill_count是告诉zfill函数总共数字是几位的，需要补几个0，最后统一格式比如3位：001，010，100。。。。
def get_attribute_metadata(metadata_path):

    # Read attribute data from metadata file 
    df = pd.read_csv(metadata_path)
    df = df.drop('Unnamed: 0', axis = 1)
    df.columns = [clean_attributes(col) for col in df.columns]

    # Get zfill count based on number of images generated
    zfill_count = len(str(df.shape[0]))


    return df, zfill_count

# Main function that generates the JSON metadata
# 生成 JSON 元数据的主函数
def main():

    # Get edition name
    print("Enter edition you want to generate metadata for: ")
    while True:
        edition_name = input()
        edition_path, metadata_path, json_path = generate_paths(edition_name)

        if os.path.exists(edition_path):
            print("Edition exists! Generating JSON metadata...")
            break
        else:
            print("Oops! Looks like this edition doesn't exist! Check your output folder to see what editions exist.")
            print("Enter edition you want to generate metadata for: ")
            continue
    
    # Make json folder
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    
    # Get attribute data and zfill count
    # 获取属性数据和 zfill 计数
    df, zfill_count = get_attribute_metadata(metadata_path)


    for idx, row in df.iterrows():
    
        # Get a copy of the base JSON (python dict)
        item_json = deepcopy(BASE_JSON)
        
        # Append number to base name
        item_json['name'] = item_json['name'] + str(idx+1)

        # Append image PNG file name to base image path
        item_json['image'] = item_json['image'] + '/' + str(idx+1).zfill(zfill_count) + '.png'

        # Convert pandas series to dictionary
        attr_dict = dict(row)
        
        # Add all existing traits to attributes dictionary
        # 将所有现有特征添加到属性字典
        for attr in attr_dict:
            
            if attr_dict[attr] != 'none':
                item_json['attributes'].append({ 'trait_type': attr, 'value': attr_dict[attr] })
        
        # Write file to json folder
        item_json_path = os.path.join(json_path, str(idx+1) + '.json')
        with open(item_json_path, 'w') as f:
            json.dump(item_json, f)

# Run the main function
main()