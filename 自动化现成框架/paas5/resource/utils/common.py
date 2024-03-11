import time

# import allure
import allure
import requests
import json
import jsonpath
import string
import random


def get_value_from_json(json_data, json_path, list_flag=False):
    """
    利用jsonpath表达式取值
    :param json_data: (*)取值对象, 可以是requests.Response对象, json格式字符串, 字典, 数组
    :param json_path: (*)jsonpath表达式
    :param list_flag: 列表标识, 默认为False, 返回匹配结果集中的第一个元素; 为True则返回整个匹配结果集列表
    :return: jsonpath匹配结果
    :raise TypeError: 传入的json_data不符合JSON格式
    :raise AssertionError: 当value_name非空, jsonpath匹配结果为空
    :author: zhaozhipeng19872 2021.02.20
    """
    if isinstance(json_data, requests.Response):
        json_data = json_data.text
    if not (isinstance(json_data, dict) or isinstance(json_data, list)):
        try:
            json_data = json.loads(json_data)
        except Exception as e:
            raise Exception("传入的参数不是JSON字典{}".format(json_data))
    value_list = jsonpath.jsonpath(json_data, json_path)

    if isinstance(value_list, list) and (not list_flag):
        return value_list[0]

    return value_list


def check_status_code(response, expect_code=200):
    """
    校验状态码
    :param response: request.Response对象
    :param expect_code: 预期状态, 默认值为200
    :return: 无
    :raise AssertionError: 状态码不满足预期
    """
    if isinstance(expect_code, str):
        expect_code = int(expect_code)
    status_code = response.status_code
    assert status_code == expect_code, "预期状态码为:{expect_code}, 实际状态码为:{status_code}, 消息体为:{content}".format(
        expect_code=expect_code, status_code=status_code, content=response.text)


def check_response_status(response, expect_code=200):
    """
    校验状态码和response中的status字段
    :param response: request.Response对象
    :param expect_code: 预期状态, 默认值为200
    :return: 无
    :raise AssertionError: 状态码不满足预期
    """
    # 校验状态码
    check_status_code(response, expect_code)
    # 校验response中的status字段为True
    response_status = get_value_from_json(response, "$..status")
    response_msg = get_value_from_json(response, "$..msg")
    assert response_status is True, "操作失败, {}".format(response_msg)


def check_response(exp_response, act_response):
    """
    校验状response中的指定字段

    :param exp_response: 期望的key和value。
    :param act_response: request.Response.text对象
    :return: 无
    :raise AssertionError: 不满足预期
    """
    for exp_key in exp_response:
        if (exp_key in act_response) & (exp_response[exp_key] == act_response[exp_key]):
            continue
        else:
            raise Exception(f"响应校验失败。\n期望响应：{exp_response}\n实际响应：{act_response}")


def get_random_string(length, char_type=0):
    """
    获取定义个数的随机字符串
    :param length: 随机字符个数
    :param char_type: 随机字符类型。0：英文字符；1：中文字符；2：中英文和特殊字符混合; 3：英文+数字
    :return: 定义个数的随机字符
    """
    if isinstance(length, str):
        length = int(length)
    assert isinstance(length, int)

    # 中文字符
    chinese_str = '长风破浪会有时直挂云帆济沧海自己动手丰衣足食志当存高远'
    chn_str = ''
    for i in range(length):
        chn_str += random.choice(chinese_str)
    # for i in range(length):
    #     head = random.randint(0xb0, 0xf7)
    #     body = random.randint(0xa1, 0xfe)
    #     val = f'{head:x}{body:x}'
    #     chn_str += bytes.fromhex(val).decode('gbk')

    # 特殊字符
    special_str = "`~!@#$%^&*()_+{}|:\"<>?/.,\';\\][=-"
    spec_str = ''
    for i in range(length):
        spec_str += random.choice(special_str)

    if char_type == 0:
        return ''.join(random.sample(string.ascii_letters, length))
    elif char_type == 1:
        return chn_str
    elif char_type == 2:
        return ''.join(random.sample(string.ascii_letters + chn_str + spec_str, length))
    else:
        nums = random.randint(0, 9)
        return ''.join(random.sample(string.ascii_letters + str(nums), length))


def check_status_timeout(exp, act_path, func, timeout=300, **kwargs):
    """
    超时处理。对比的是从返回的json字符串中获取的status

    :param exp: 期望状态
    :param act_path: 实际状态的path表达式
    :param func: 取值函数
    :param timeout: 超时时间。缺省为5min
    :param kwargs: 函数中传递的参数
    :return:
    """
    temp = timeout / 5
    cnt = 1
    while cnt <= temp:
        time.sleep(5)
        result = func(**kwargs)
        if len(result['data']) > 0:
            act = jsonpath.jsonpath(result, act_path)[0]
            if act == exp:
                break
        cnt = cnt + 1
    if cnt > temp:
        raise Exception(f"超时")


def check_del_result_timeout(func, timeout=300, **kwargs):
    """
    删除资源时的超时处理。

    :param func: 取值函数
    :param timeout: 超时时间。缺省为5min
    :param kwargs: 函数中传递的参数
    :return:
    """
    temp = timeout / 5
    cnt = 1
    while cnt <= temp:
        time.sleep(5)
        result = func(**kwargs)
        if len(result['data']) == 0:
            break
        cnt = cnt + 1
    if cnt > temp:
        raise Exception(f"超时")


def check_message_timeout(exp, func, timeout=300, **kwargs):
    """
    超时处理。对比的是从返回的json字符串中获取的status

    :param exp: 期望信息
    :param func: 取值函数
    :param timeout: 超时时间。缺省为5min
    :param kwargs: 函数中传递的参数
    :return:
    """
    temp = timeout / 5
    cnt = 1
    while cnt <= temp:
        time.sleep(5)
        act = func(**kwargs)
        if act == exp:
            break
        cnt = cnt + 1
    if cnt > temp:
        raise Exception(f"超时")


def check_contained_message_timeout(exp, func, timeout=300, **kwargs):
    """
    超时处理。对比响应中是否包含有指定信息

    :param exp: 期望信息
    :param func: 取值函数
    :param timeout: 超时时间。缺省为5min
    :param kwargs: 函数中传递的参数
    :return:
    """
    temp = timeout / 5
    cnt = 1
    while cnt <= temp:
        time.sleep(5)
        act = func(**kwargs)
        if exp in act:
            break
        cnt = cnt + 1
    if cnt > temp:
        raise Exception(f"超时")


def show_testcase_title(title):
    """
    显示用例标题

    :param title: 用例标题
    """
    allure.dynamic.title(title)


def query_until_timeout(query_request, expect_code: bool, value_jsonpath=None, expect_value=None, timeout=300):
    """等待微服务引擎等资源创建或者删除完成 成功创建或删除则返回True 超时失败则返回False
    Args:
        query_request : 
        
    """
    cnt = 0
    while cnt < timeout:
        time.sleep(5)
        result = query_request()
        if expect_code and bool(result):
            if get_value_from_json(result, value_jsonpath) == expect_value:
                return True
        if not (bool(result) or expect_code):
            return True
        cnt = cnt + 5
    return False

