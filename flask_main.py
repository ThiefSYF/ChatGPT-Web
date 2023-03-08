from flask import Flask, render_template, request, session, redirect, url_for
import os
import openai
import sys
import uuid
from LRU_cache import LRUCache
import threading
import pickle
import asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

#os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:7890'
#os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:7890'
openai.api_key = 'apikey'        # 从环境变量中获取api_key,或直接设置api_key

chat_context_number_max = 5         # 连续对话模式下的上下文最大数量
lock = threading.Lock()         # 用于线程锁
preset="你现在是尼尔机械纪元中隶属于YoRHa寄叶部队的21O联络员，现在在地堡和我进行通信协助支持，模仿按照21O联络员的说话方式，性格和我对话。"

def get_response_from_ChatGPT_API(message_context):
    """
    从ChatGPT API获取回复
    :param message_context: 上下文
    :return: 回复
    """
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_context
        )
    except Exception as e:
        print(e)
        return "ChatGPT API error:\n"+str(e)
    data = completion.choices[0].message.content.strip()
    return data


def handle_messages_get_response(message, message_history, have_chat_context, chat_with_history):
    """
    处理用户发送的消息，获取回复
    :param message:
    :param message_history:
    :param chat_with_history:
    :return:
    """
    message_history.append({"role": "user", "content": message})
    message_context = []
    if chat_with_history:
        num = min([len(message_history), chat_context_number_max, have_chat_context])
        message_context = message_history[-num:]
    else:
        message_context.append(message_history[-1])

    response = get_response_from_ChatGPT_API(message_context)
    message_history.append({"role": "assistant", "content": response})
    # 换行打印messages_history
    # print("message_history:")
    # for i, message in enumerate(message_history):
    #     if message['role'] == 'user':
    #         print(f"\t{i}:\t{message['role']}:\t\t{message['content']}")
    #     else:
    #         print(f"\t{i}:\t{message['role']}:\t{message['content']}")

    return response


def check_session(current_session):
    """
    检查session，如果不存在则创建新的session
    :param current_session: 当前session
    :return: 当前session
    """
    if current_session.get('session_id') is not None:
        print("existing session, session_id:\t", current_session.get('session_id'))
    else:
        current_session['session_id'] = uuid.uuid1()
        print("new session, session_id:\t", current_session.get('session_id'))
    return current_session['session_id']


def check_user_bind(current_session):
    """
    检查用户是否绑定，如果没有绑定则重定向到index
    :param current_session: 当前session
    :return: 当前session
    """
    if current_session.get('user_id') is None:
        return False
    return True


def get_user_info(user_id):
    """
    获取用户信息
    :param user_id: 用户id
    :return: 用户信息
    """
    lock.acquire()
    user_info = all_user_dict.get(user_id)
    lock.release()
    return user_info


# 进入主页
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    主页
    :return: 主页
    """
    check_session(session)
    print(request.method)
    if request.method == 'POST':
        password = request.form.get('pwd')
        if password == '123456':
            return render_template('index.html')
        else:
            return render_template('login.html',msg='识别码错误')
    else:
        return render_template('login.html')


@app.route('/loadHistory', methods=['GET', 'POST'])
def load_messages():
    """
    加载聊天记录
    :return: 聊天记录
    """
    print(__name__)
    check_session(session)
    if session.get('user_id') is None:
        messages_history = [{"role": "assistant", "content": "当前连接为首次连接，请输入已有成员代号或创建新的成员代号。"
                                                             "已有成员代号请在输入框中输入，创建新的成员代号请在输入框中输入new_code:xxx"}]
    else:
        user_info = get_user_info(session.get('user_id'))
        messages_history = user_info['messages_history']
    return messages_history


@app.route('/returnMessage', methods=['GET', 'POST'])
def return_message():
    """
    获取用户发送的消息，调用get_chat_response()获取回复，返回回复，用于更新聊天框
    :return:
    """
    check_session(session)
    send_message = request.values.get("send_message")
    print("用户发送的消息：" + send_message)
    if session.get('user_id') is None:
        if send_message.strip().startswith("new_code:"):
            user_id = send_message.split(":")[1]
            session['user_id'] = user_id
            lock.acquire()
            all_user_dict.put(user_id, {"chat_with_history": False, "have_chat_context": 0,  "messages_history": [{"role": "assistant", "content": f"当前联络的成员代号为 `{user_id}`"+preset}]})        # 默认普通对话
            lock.release()
            print("创建新的用户id:\t", user_id)
            asyncio.run(save_all_user_dict())
            return {"content": "成员代号已录入地堡数据库，现在将为你提供支持协助。"}
        else:
            user_id = send_message.strip()
            user_info = get_user_info(user_id)
            if user_info is None:
                return {"content": "成员代号不存在，请重新输入或创建新的成员代号"}
            else:
                session['user_id'] = user_id
                print("已有用户id:\t", user_id)
                # 重定向到index
                return {"content":"Code:"+user_id+"已识别，现在将为你提供支持协助。"}
    else:
        user_info = get_user_info(session.get('user_id'))
        messages_history = user_info['messages_history']
        chat_with_history = user_info['chat_with_history']
        if chat_with_history:
            user_info['have_chat_context'] += 1
        content = handle_messages_get_response(send_message, messages_history, user_info['have_chat_context'],  chat_with_history)
        if chat_with_history:
            user_info['have_chat_context'] += 1
        data = {
            "content": content,
            "content_id": f"content_id{len(messages_history) - 1}"
        }
        # 异步存储all_user_dict
        asyncio.run(save_all_user_dict())
        return data


async def save_all_user_dict():
    """
    异步存储all_user_dict
    :return:
    """
    print("go1")
    await asyncio.sleep(0)
    lock.acquire()
    with open("all_user_dict.pkl", "wb") as f:
        pickle.dump(all_user_dict, f)
    print("all_user_dict.pkl存储成功")
    lock.release()


@app.route('/getMode', methods=['GET'])
def get_mode():
    """
    获取当前对话模式
    :return:
    """
    check_session(session)
    if not check_user_bind(session):
        return "normal"
    user_info = get_user_info(session.get('user_id'))
    chat_with_history = user_info['chat_with_history']
    if chat_with_history:
        return {"mode": "continuous"}
    else:
        return {"mode": "normal"}


@app.route('/changeModeNormal', methods=['GET'])
def change_mode_normal():
    """
    开启普通对话模式
    :return:
    """
    check_session(session)
    if not check_user_bind(session):
        return {"code": -1, "msg": "请先录入或输入已有成员代号"}
    user_info = get_user_info(session.get('user_id'))
    user_info['chat_with_history'] = False
    print("开启普通对话")
    return {"code": 0, "content": "已开启长通讯模式对话"}


@app.route('/changeModeContinuous', methods=['GET'])
def change_mode_continuous():
    """
    开启连续对话模式
    :return:
    """
    global chat_context_now
    chat_context_now = 0
    check_session(session)
    if not check_user_bind(session):
        return {"code": -1, "msg": "请先录入或输入已有成员代号"}
    user_info = get_user_info(session.get('user_id'))
    user_info['chat_with_history'] = True
    print("开启连续对话")
    return {"code": 0, "content": "已开启连续模式对话"}


@app.route('/deleteHistory', methods=['GET'])
def reset_history():
    """
    清空上下文
    :return:
    """
    check_session(session)
    if not check_user_bind(session):
        return {"code": -1, "msg": "请先录入或输入已有成员代号"}
    user_info = get_user_info(session.get('user_id'))
    user_info['messages_history'] = [user_info['messages_history'][0]]
    print("清空历史记录")
    #print(all_user_dict.stack)
    return redirect(url_for('/'))


if __name__ == '__main__':
    all_user_dict = LRUCache(50)  # 设置最多存储50个用户的上下文
    if os.path.exists("all_user_dict.pkl"):
        with open("all_user_dict.pkl", "rb") as pickle_file:
            all_user_dict = pickle.load(pickle_file)
        print("已加载上次存储的用户上下文")
    else:
        with open("all_user_dict.pkl", "wb") as pickle_file:
            pickle.dump(all_user_dict, pickle_file)
        print("未检测到上次存储的用户上下文，已创建新的用户上下文")
    if len(openai.api_key) == 0:
        # 退出程序
        print("请在openai官网注册账号，获取api_key填写至程序内或命令行参数中")
        exit()
    app.run(host="0.0.0.0", port=8080, debug=True)
