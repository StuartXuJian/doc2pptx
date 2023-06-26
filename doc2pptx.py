import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染

import gradio as gr
import langchain

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate 
)

## configuration files, which to be put into a separated file

# [step 1]>> 例如： API_KEY = "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" （此key无效）
API_KEY = "sk-K2dwXy8hX5IHItiAZS1Ik7hNSEiGxR5AE2GTF71q9WffwSE4"    # 可同时填写多个API-KEY，用英文逗号分割，例如API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey1,fkxxxx-api2dkey2"

# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改
USE_PROXY = False
if USE_PROXY:
    # 填写格式是 [协议]://  [地址] :[端口]，填写之前不要忘记把USE_PROXY改成True，如果直接在海外服务器部署，此处不修改
    # 例如    "socks5h://localhost:11284"
    # [协议] 常见协议无非socks5h/http; 例如 v2**y 和 ss* 的默认本地协议是socks5h; 而cl**h 的默认本地协议是http
    # [地址] 懂的都懂，不懂就填localhost或者127.0.0.1肯定错不了（localhost意思是代理软件安装在本机上）
    # [端口] 在代理软件的设置里找。虽然不同的代理软件界面不一样，但端口号都应该在最显眼的位置上

    # 代理网络的地址，打开你的*学*网软件查看代理的协议(socks5/http)、地址(localhost)和端口(11284)
    proxies = {
        #          [协议]://  [地址]  :[端口]
        "http": "http://10.144.1.10:8080",
        "https": "http://10.144.1.10:8080",
    }
else:
    proxies = None

# 对话窗的高度
CHATBOT_HEIGHT = 600

# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = 30

# 网页的端口, -1代表随机端口
WEB_PORT = 18888

# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = 2

# 模型选择是 (注意: LLM_MODEL是默认选中的模型, 同时它必须被包含在AVAIL_LLM_MODELS切换列表中 )
LLM_MODEL = "gpt-3.5-turbo" # 可选 ↓↓↓

# 设置gradio的并行线程数（不需要修改）
CONCURRENT_COUNT = 100

# 设置是否用FreeGPT
FreeGPT = True

def update_ui(chatbot, history, msg='Normal', **kwargs):  # 刷新界面
    yield chatbot, history, msg, ""


def new_predict(txt, chatbot, history):
    
    history.append(txt)
    chatbot.append([txt,"GPT思考中......请给它一点时间思考"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "Please reply always in Markdown format."
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    #请以```来形成代码段的方式，提供代码，请以markdown·格式代码段的方式来写

    if FreeGPT:
        api_base = "https://api.chatanywhere.com.cn/v1"
    else:
        api_base = "https://api.openai.com/v1/"


    langchain.debug = True
    llm = ChatOpenAI(temperature=0, openai_api_base=api_base, openai_api_key=API_KEY, proxies=proxies)
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    gpt_says = conversation.predict(input=txt)
    print(gpt_says)
    

    history.append(gpt_says)
    chatbot[-1]=[history[-2], history[-1]]
    
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


def main():
    title = "PPTX generator"

    title_html = f"<h1 align=\"center\">{title}</h1>"
    "<h3 align=\"center\" style=\"font-weight: bold; color: red;\">Notice: Make sure no private data input -- data will be transferred to LLM(e.g. chatGPT) </h3>"
    
    with gr.Blocks(title=f"{title}", analytics_enabled=False) as index:
        gr.HTML(title_html)
        cookies = gr.State({'api_key': API_KEY, 'llm_model': LLM_MODEL})

        cancel_handles = []
        with gr.Row().style():
            chatbot = gr.Chatbot(label=f"LLM：{LLM_MODEL}")
            chatbot.style(height=CHATBOT_HEIGHT)
            history = gr.State([])
        with gr.Row().style():
            with gr.Accordion("Please input your speech here:", open=True) as area_input_primary:
                with gr.Row():
                    txt = gr.Textbox(show_label=False, placeholder="Input question here.").style(container=False)
                with gr.Row():
                    submitBtn = gr.Button("Submit", variant="primary")
                with gr.Row():
                    resetBtn = gr.Button("Reset", variant="secondary"); resetBtn.style(size="sm")
                    stopBtn = gr.Button("Stop", variant="secondary"); stopBtn.style(size="sm")
                    clearBtn = gr.Button("Clear", variant="secondary", visible=True); clearBtn.style(size="sm")
                with gr.Row():
                    status = gr.Markdown(f"Tips: Submit with \"Enter\" directly, new line with \"Shift+Enter\"。")

        
        # 整理反复出现的控件句柄组合
        input_combo = [txt, chatbot, history]
        output_combo = [chatbot, history, status, txt]

        predict_args = dict(fn=new_predict, inputs=input_combo, outputs=output_combo)
        # 提交按钮、重置按钮
        cancel_handles.append(txt.submit(**predict_args))
        cancel_handles.append(submitBtn.click(**predict_args))
        resetBtn.click(lambda: ([], [], "Session Reseted"), None, [chatbot, history, status])
        clearBtn.click(lambda: ("", "Input Cleared"), None, [txt, status])
        # 终止按钮的回调函数注册
        stopBtn.click(fn=None, inputs=None, outputs=None, cancels=cancel_handles)

    print(f"http://localhost:{WEB_PORT} Started...")
    index.queue(concurrency_count=CONCURRENT_COUNT).launch(
        server_name="0.0.0.0", server_port=WEB_PORT,
        favicon_path="docs/logo.png",
        blocked_paths=["config.md"])



if __name__ == "__main__":
    main()