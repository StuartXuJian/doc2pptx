# Doc2pptx

<p align="center">
   🌐 一个PPT初始化小工具[Doc2pptx]</a> <a href="https://github.com/StuartXuJian/doc2pptx" target="_blank">[GitHub]</a> <br>
</p>

*Read this in [English](README_en.md).*

要解决的用户痛点：

- 作为管理者，通常我会被要求为某人(例如我的老板或团队成员)创建报告，PPTX通常是一个很好的结构化方式来展示我的想法。但是，用格式编写PPTX是很枯燥的。在报告结束后，我还被期望创建一个Yammer来发布更多信息。
- 作为培训师，我对于使用收集到的数据和将我的思想结构化以满足特定受众的需求来创建PPTX感到厌烦。


方案：

- 将所有材料放入LLM中，并期望它能生成Markdown的论文大纲。
- 将Markdown转换为PPTX。












---
Thanks to below project owner.
This is major project I have used in this project.

Markdown to Powerpoint Converter

**Note:** md2pptx only supports Python 3. So the installation instructions are for that.

**Usage:**

  `python3 md2pptx output.pptx < input.markdown`

or

  `md2pptx output.pptx < input.markdown`

### Installation

Installation is straightforward:

1. Install python-pptx
2. Clone md2pptx into a new directory

The md2pptx repo includes all the essentials, such as funnel.py. You don't install these with eg pip. There are some optional packages, outlined in the User Guide.

You can install python-pptx with

  `pip3 install python-pptx`

(On a Raspberry Pi you might want to use `pip3` (or `python3 -m pip`) to install for Python 3.)

You will probably need to issue the following command from the directory where you install it:

  `chmod +x md2pptx`

### Starting To Use md2pptx

I would also suggest you start with a presentation that references Martin Template.pptx in the metadata (before the first blank line). \
Here is a very simple deck that does exactly that.

```
template: Martin Template.pptx

# This Is A Presentation Title Page

## This Is A Presentation Section Page

### This Is A Bulleted List Page

* One
    * One A
    * One B
* Two

Here are some slide notes. Note you leave an empty line between the content - in this case a bulleted list - and the notes.

You can do multiple paragraphs and even use symbols.
```

