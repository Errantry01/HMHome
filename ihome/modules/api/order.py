import datetime

from ihome import db, sr
from ihome.models import House, Order
from ihome.utils.common import login_required
from ihome.utils.response_code import RET
from . import api_blu
from flask import request, g, jsonify, current_app, session


# 预订房间
@api_blu.route('/orders', methods=['POST'])
@login_required
def add_order():
    """
    下单
    1. 获取参数
    2. 校验参数
    3. 查询指定房屋是否存在
    4. 判断当前房屋的房主是否是登录用户
    5. 查询当前预订时间是否存在冲突
    6. 生成订单模型，进行下单
    7. 返回下单结果
    :return:
    """
    param_dict = request.json
    start_date = param_dict.get('start_date')
    end_date = param_dict.get('end_date')
    house_id = param_dict.get('house_id')
    user_id = g.user_id

    # 校验参数
    if not all([start_date, end_date, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')

    # 查询房屋是否存在
    try:
        house = House.query.filter(House.id == house_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋数据异常")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 判断当前房屋的房主是否是登录用户
    if user_id == house.user_id:
        return jsonify(errno=RET.DATAERR, errmsg='用户为屋主,不能预定')

    # 查询当前预订时间是否存在冲突
    try:
        order = Order.query.filter(Order.house_id == house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询订单数据异常")
    if order:
        if not (start_date > order.end_date or end_date < order.begin_date):
            return jsonify(errno=RET.DATAERR, errmsg='该时间段已有订单')

    # 生成订单模型，进行下单
    order = Order()
    order.user_id = user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存订单数据异常")
    # 返回数据
    return {"data": {"order_id": order.id},
            "errno": "0",
            "errmsg": "OK"}


# 获取我的订单
@api_blu.route('/orders')
@login_required
def get_orders():
    """
    1. 去订单的表中查询当前登录用户下的订单
    2. 返回数据
    :return:
    """
    # 1获取参数

    comment = request.args.get('comment')
    if comment == 'landlord':
        return current_app.send_static_file("ihome/static/html/lorders.html")
    elif comment == 'custom':
        pass



# 接受/拒绝订单
@api_blu.route('/orders', methods=["PUT"])
@login_required
def change_order_status():
    """
    1. 接受参数：order_id
    2. 通过order_id找到指定的订单，(条件：status="待接单")
    3. 修改订单状态
    4. 保存到数据库
    5. 返回
    :return:
    """
    pass


# 评论订单
@api_blu.route('/orders/comment', methods=["PUT"])
@login_required
def order_comment():
    """
    订单评价
    1. 获取参数
    2. 校验参数
    3. 修改模型
    :return:
    """
    pass
