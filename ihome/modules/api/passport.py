# 实现图片验证码和短信验证码的逻辑
import re, random
from flask import request, abort, current_app, jsonify, make_response, json, session
from datetime import datetime
from ihome import sr, db
from ihome.libs.captcha.pic_captcha import captcha
from ihome.libs.yuntongxun.sms import CCP
from ihome.models import User
from ihome.modules.api import api_blu
from ihome.utils import constants
from ihome.utils.response_code import RET


# 获取图片验证码
@api_blu.route("/imagecode")
def get_image_code():
    """
    1. 获取传入的验证码编号，并编号是否有值
    2. 生成图片验证码
    3. 保存编号和其对应的图片验证码内容到redis
    4. 返回验证码图片
    :return:
    """
    pass



# 获取短信验证码
@api_blu.route('/smscode', methods=["POST"])
def send_sms():
    """
    1. 接收参数并判断是否有值
    2. 校验手机号是正确
    3. 通过传入的图片编码去redis中查询真实的图片验证码内容
    4. 进行验证码内容的比对
    5. 生成发送短信的内容并发送短信
    6. redis中保存短信验证码内容
    7. 返回发送成功的响应
    :return:
    """
    pass



# 用户注册
@api_blu.route("/user", methods=["POST"])
def register():
    """
    1. 获取参数和判断是否有值
    2. 从redis中获取指定手机号对应的短信验证码的
    3. 校验验证码
    4. 初始化 user 模型，并设置数据并添加到数据库
    5. 保存当前用户的状态
    6. 返回注册的结果
    :return:
    """
    pass


# 用户登录
@api_blu.route("/session", methods=["POST"])
def login():
    """
    1. 获取参数和判断是否有值
    2. 从数据库查询出指定的用户
    3. 校验密码
    4. 保存用户登录状态
    5. 返回结果
    :return:
    """
    pass


# 获取登录状态
@api_blu.route('/session')
def check_login():
    """
    检测用户是否登录，如果登录，则返回用户的名和用户id
    :return:
    """
    pass


# 退出登录
@api_blu.route("/session", methods=["DELETE"])
def logout():
    """
    1. 清除session中的对应登录之后保存的信息
    :return:
    """
    pass


# 登录页面发送短信验证码
@api_blu.route('/login_send_sms', methods=['POST'])
def login_send_sms():
    # 1. 接收参数并判断是否有值
    mobile = request.json.get('mobile')

    if not mobile:
        current_app.logger.error('参数不足')
        return jsonify(errno=RET.PARAMERR, errmsg='请输入手机号码')
    # 2. 校验手机号是正确
    if not re.match(r"1[2345678][0-9]{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号码格式错误")

    # 3. 生成发送短信的内容并发送短信
    # TODO: 判断手机号码是否已经注册 【提高用户体验】
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户数据异常")

    if not user:
        # 当前手机号码未注册
        return jsonify(errno=RET.USERERR, errmsg="当前手机号码未注册")

        # 3.4.1 生成6位的随机短信
    real_sms_code = random.randint(0, 999999)
    # 6位，前面补零
    real_sms_code = "%06d" % real_sms_code
    # 4.发送短信验证码成功
    try:
        result = CCP().send_template_sms(mobile, {real_sms_code, 5}, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="云通信发送短信验证码异常")
    # 发送短信验证码失败：告知前端
    if result == -1:
        return jsonify(errno=RET.THIRDERR, errmsg="云通信发送短信验证码异常")
    # 6. redis中保存短信验证码内容
    sr.setex("SMS_CODE_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, real_sms_code)
    # 7. 返回发送成功的响应
    return jsonify(errno=RET.OK, errmsg="发送短信验证码成功")


@api_blu.route('/login_sms', methods=['POST'])
def login_sms():
    # 1. 获取参数和判断是否有值

    mobile = request.json.get("mobile")
    phonecode = request.json.get("phonecode")

    if not all([mobile, phonecode]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 从数据库查询出指定的用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询用户对象异常")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="当前手机号码未注册")

    try:
        real_sms_code = sr.get("SMS_CODE_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询redis中短信验证码异常")

    # 3. 校验验证码
    if phonecode != real_sms_code:
        #  3.3 不相等：短信验证码填写错误
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码填写错误")

    # 4. 保存用户登录状态

    session["user_id"] = user.id
    session["mobile"] = user.mobile

    # 记录用户最后一次登录时间
    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库保存用户信息异常')

    # 5. 登录成功
    return jsonify(errno=RET.OK, errmsg="OK")



