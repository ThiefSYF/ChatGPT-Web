# 使用最新ChatGPT最新API创建的聊天页面，模型回复效果与官网的ChatGPT一致
## 注册openai后送18美元，3个月内使用，API调用，0.2美分1000 token

## 更新说明
> 2023.3.5: 支持markdown内容显示   
> 2323.3.6: 支持保存历史聊天记录，当重新打开会话时自动恢复聊天记录,使用pickle持久化存储  
> 2323.3.6: 会话与用户id绑定，其余设备输入用户id后依然可以重载聊天记录  

## 使用前提
> 1. 因国内IP被封或OpenAI API被墙，因此自己需要有代理，稍后需要配置  
> 2. 有openai账号，注册事项可以参考[此文章](https://juejin.cn/post/7173447848292253704)   
> 3. 创建好api_key, 进入[OpenAI链接](https://platform.openai.com/),右上角点击，进入页面设置  
![image](https://user-images.githubusercontent.com/38237931/222461544-260ef350-2d05-486d-bf36-d078873b0f7a.png)


## 使用方法
1. 执行`pip install openai` `pip install flask`安装必要包
2. 打开`flask_main.py`文件
3. 将`openai.api_key`填写为自己的api key
4. 将os.environ['HTTP_PROXY']和os.environ['HTTPS_PROXY']设置成代理，注意端口设置
5. 执行`python flask_main.py`运行程序.若程序中未指定apikey还可以执行`OPANAI_API_KEY=XXXX python flask_main.py`来指定，其中XXXX为你的apikey
6. 打开本地浏览器访问`127.0.0.1:5000`


## 介绍
- 开启程序后进入如下页面  
![image](https://user-images.githubusercontent.com/38237931/223034501-13881560-5da6-4897-833d-46e5babdcfcb.png)
- 输入已有用户id,或者输入new_id:xxx创建新id，这个id用于绑定会话，下次不同浏览器打开都可以恢复用户的聊天记录,如下为创建一个新id，一个浏览器31天内不会要求再次输入用户id
![image](https://user-images.githubusercontent.com/38237931/223035594-31479a0e-25ec-462a-85e4-80694ea7d0d9.png)
- 默认为普通对话模式，即每次发送都是仅对于该提问回答，可点击切换为连续对话模式，chatgpt将会联系上下文(之前的对话，程序中设置了最大5条记录)回复你，但意味着花费会更多money  
- 用python写一个冒泡算法试试看，回车发送，shift+回车换行  
- 然后问用C语言呢？会联系上下文回答 
![image](https://user-images.githubusercontent.com/38237931/223036485-82340df2-9cd5-4ba6-ac55-62cb4aa52926.png)

## TODO List
- [ ] 界面优化
- [ ] 优化代码显示
- [x] 在连续对话模式下支持多人同时使用
- [x] 重载历史记录
- [x] 切换聊天模式和重置时提示
- [ ] 公式显示
