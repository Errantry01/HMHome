import datetime

from flask import current_app, jsonify, request, g, session
from ihome import sr, db
from ihome.models import Area, House, Facility, HouseImage, Order, User
from ihome.modules.api import api_blu
from ihome.utils import constants
from ihome.utils.common import login_required
from ihome.utils.constants import AREA_INFO_REDIS_EXPIRES, QINIU_DOMIN_PREFIX, HOUSE_LIST_PAGE_CAPACITY, \
    HOME_PAGE_MAX_HOUSES, HOME_PAGE_DATA_REDIS_EXPIRES
from ihome.utils.image_storage import storage_image
from ihome.utils.response_code import RET


# 我的发布列表
@api_blu.route('/user/houses')
@login_required
def get_user_house_list():
    """
    获取用户房屋列表
    1. 获取当前登录用户id
    2. 查询数据
    :return:
    """
    # 获取登录用户的id
    user_id = g.user_id

    # 查询数据
    houses = []
    try:
        houses = House.query.filter(House.user_id == user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋数据异常")

    # 获取房屋信息
    for house in houses:
        try:
            house_area = Area.query.filter(house.area_id == Area.id).first()
            house_image = HouseImage.query.filter(house.id == HouseImage.house_id).first()
            house_user = User.query.filter(User.id == house.user_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="查询用户数据异常")
        data = {'data': [{"address": house.address,
                          "area_name": house_area.name,
                          "ctime": house.create_time,
                          "house_id": house.id,
                          "img_url": house_image.url,
                          "order_count": house.order_count,
                          "price": house.price,
                          "room_count": house.room_count,
                          "title": house.title,
                          "user_avatar": house_user.avatar_url}]
                }
        return {'data': data,
                "errno": "0",
                "errmsg": "OK"
                }


# 获取地区信息
@api_blu.route("/areas")
def get_areas():
    """
    1. 查询出所有的城区
    2. 返回
    :return:
    """
    pass

# 上传房屋图片
@api_blu.route("/houses/<int:house_id>/images", methods=['POST'])
@login_required
def upload_house_image(house_id):
    """
    1. 取到上传的图片
    2. 进行七牛云上传
    3. 将上传返回的图片地址存储
    4. 进行返回
    :return:
    """
    pass


# 发布房源
@api_blu.route("/houses", methods=["POST"])
@login_required
def save_new_house():
    """
    1. 接收参数并且判空
    2. 将参数的数据保存到新创建house模型
    3. 保存house模型到数据库
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    :return:
    """
    pass


# 房屋详情
@api_blu.route('/houses/<int:house_id>')
def get_house_detail(house_id):
    """
    1. 通过房屋id查询出房屋模型
    :param house_id:
    :return:
    """
    pass


# 获取首页展示内容
@api_blu.route('/houses/index')
def house_index():
    """
    获取首页房屋列表
    :return:
    """
    pass


# 搜索房屋/获取房屋列表
@api_blu.route('/houses')
def get_house_list():
    pass
