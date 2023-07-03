import os; 
# os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染

import gradio as gr
import langchain
import re
import datetime

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate 
)

from mdr2pptx import convert
import traceback

## configuration files, which to be put into a separated file

# [step 1]>> 例如： API_KEY = "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" （此key无效）
API_KEY = "sk-K2dwXy8hX5IHItiAZS1Ik7hNSEiGxR5AE2GTF71q9WffwSE4"    # 可同时填写多个API-KEY，用英文逗号分割，例如API_KEY = "sk-openaikey1,sk-openaikey2,fkxxxx-api2dkey1,fkxxxx-api2dkey2"

# [step 2]>> 改为True应用代理，如果直接在海外服务器部署，此处不修改
USE_PROXY = False

# 对话窗的高度
CHATBOT_HEIGHT = 600

# 发送请求到OpenAI后，等待多久判定为超时
TIMEOUT_SECONDS = 30

# 网页的端口, -1代表随机端口
WEB_PORT = 18880

# 如果OpenAI不响应（网络卡顿、代理失败、KEY失效），重试的次数限制
MAX_RETRY = 2

# 模型选择是 (注意: LLM_MODEL是默认选中的模型, 同时它必须被包含在AVAIL_LLM_MODELS切换列表中 )
LLM_MODEL = "gpt-3.5-turbo" # 可选 ↓↓↓

# 设置gradio的并行线程数（不需要修改）
CONCURRENT_COUNT = 100

# 设置是否用FreeGPT
FREEGPT_INUSE = True

# 从GPT返回的内容中提取Markdown的内容
def extractMarkDownContent(inputStr:str)->str:
    pattern = r'^```(.*?)```$'
    match = re.search(pattern, inputStr, re.MULTILINE)
    if match:
        # 输入的字符串中有代码段
        return match.group(1)
    else:
        # 输入的字符串中没有代码段，以#开头获取后面所有内容作为markdown内容
        patternMD = r'^#.*$'
        outputMD = re.findall(patternMD, inputStr, re.MULTILINE)
        if outputMD == []:
            return ""
        else:
            return outputMD.group(1)

# 强行将GPT生成的Markdown内容和要转换的格式对齐
def formatMD(inputStr:str)->str:
    lines = inputStr.split('\n')
    outputLines = ""

    if inputStr == "":
        return ""

    for i, line in enumerate(lines):
        if line.startswith("#### "):
            # ####强制改成无序列表
            outputLines += line.replace("####", "*")

        elif line.startswith("##### "):
            # #####强制改成无序列表
            outputLines += line.replace("#####", "    *")
        elif line.startswith("``"):
            # Drop unnecessary ```
            continue
        elif line.startswith("## "):
            # 当下一级直接是无序列表或者有序列表时，强制改为三级content
            nextLine = lines[i+1]
            if(nextLine.startswith("-") or nextLine.startswith("*") or nextLine.startswith("1.") or nextLine.startswith("+")):
                outputLines += line.replace("##", "###")
        else:
            outputLines += line
        outputLines += "\n"
    return outputLines

def putMDtofile(inputStr:str)->str:
    formatedStr = formatMD(inputStr)
    outputfile = f"./tmp/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

    with open(outputfile, "w", encoding="utf-8") as f:
        f.write(formatedStr)
    return outputfile


def update_ui(chatbot, history, downloadFiles=None, msg='Normal', **kwargs):  # 刷新界面
    yield chatbot, history, downloadFiles, msg, ""


def new_predict(txt, chatbot, history):
    
    history.append(txt)
    chatbot.append([txt,"PPT is generating by AI......\n\nWait a moment, usually 20~40 seconds. \n\nIf no response in 3mins, refresh the page and try again."])
    yield from update_ui(chatbot=chatbot, history=history, msg="Generating") # 刷新界面

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            '''Please reply always using unrendered markdown format in a code block (代码段), which format is using a pair of ```. 
            It's a must for you to use all 3 levels headings, and content list or even sub list under the 3rd level headings, by using a pair of ```. 
            Just the code, no other explanations.
            Here is basic grammar for markdown you need to use:
            Headings: Use '#' to indicate headings, and the number of '#' represents the heading level. One '#' is used for the first-level heading, two '#' for the second-level heading, and so on.
            Lists: Use '*' or '-' to represent unordered lists, and use numbers followed by a period to represent ordered lists.
            Output format example:
            ```
            # Title
            ## Section
            ### Subsection
            * Content
                - Explaination
                - Description
            * Content 
            * Content
                - Explaination
                - Description
            ### Subsection
            * Content
            ## Section
            ### Subsection
            * Content
            * Content 
            * Content
            ```
            '''
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    
    if FREEGPT_INUSE:
        api_base = "https://api.chatanywhere.com.cn/v1"
    else:
        api_base = "https://api.openai.com/v1/"

    if USE_PROXY:
        os.environ["http_proxy"] = "http://10.144.1.10:8080"
        os.environ["https_proxy"] = "http://10.144.1.10:8080"

    langchain.debug = False
    fileDownload = None

    try:
        llm = ChatOpenAI(temperature=0, openai_api_base=api_base, openai_api_key=API_KEY)
        memory = ConversationBufferMemory(return_messages=True)
        conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
        print(f"User input: {txt}")
        gpt_says = conversation.predict(input=txt)
        print(gpt_says)
        MarkdownFileName = putMDtofile(gpt_says)

        fileDownload = convert(MarkdownFileName)
        if fileDownload == None or "":
            gpt_says = "PPT generated Failed, please contact with tool provider to fix. Sorry for that as a new tool..."
        else:
            gpt_says = f"PPT generated, you can download it in bottom right corner: \n\n" + gpt_says
    except Exception as e:
        gpt_says = "```" + traceback.format_exc() + "```"
        print(gpt_says)

    history.append(gpt_says)
    chatbot[-1]=[history[-2], history[-1]]
    
    yield from update_ui(chatbot=chatbot, history=history, downloadFiles=fileDownload) # 刷新界面


def main():
    title = "PPTX generator"

    title_html = f"<h1 align=\"center\">{title}</h1><h3 align=\"center\" style=\"font-weight: bold; color: red;\">Notice: Make sure no private data input -- data will be transferred to LLM(e.g. chatGPT) </h3>"
    
    with gr.Blocks(title=f"{title}", analytics_enabled=False) as index:
        gr.HTML(title_html)
        cookies = gr.State({'api_key': API_KEY, 'llm_model': LLM_MODEL})

        cancel_handles = []
        with gr.Row().style():
            chatbot = gr.Chatbot(label=f"LLM:{LLM_MODEL}")
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
                with gr.Row():
                    clearBtn = gr.Button("Clear", variant="secondary", visible=True); clearBtn.style(size="sm")
                with gr.Row():
                    status = gr.Markdown(f"Tips: Submit with \"Enter\" directly, new line with \"Shift+Enter\"。")
            downloadFiles = gr.File()

        # 整理反复出现的控件句柄组合
        input_combo = [txt, chatbot, history]
        output_combo = [chatbot, history, downloadFiles, status, txt]

        predict_args = dict(fn=new_predict, inputs=input_combo, outputs=output_combo)
        # 提交按钮、重置按钮
        cancel_handles.append(txt.submit(**predict_args))
        cancel_handles.append(submitBtn.click(**predict_args))
        resetBtn.click(lambda: ([], [], "Session Reseted", None), None, [chatbot, history, status, downloadFiles])
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