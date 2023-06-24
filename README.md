# Doc2pptx


Painpoint to be resolved with this tool:
- As a manager, usually I'm asked to create report to someone (e.g. my Boss, my team), and usually PPTX is a good solution to present my idea in structure. However it's quite boring to write PPTX with format. Right after the report, I'm also expected to create a yammer to publish more information.
- As a trainer, I'm boring to create a PPTX with collected data,  and strucuture my thinking to specific audiances.



Idea:
1. Put all material to LLM, and expect it to create the essay outline in Markdown.
2. Convert Markdown to PPTX.















---
参考了以下项目，感谢项目分享者！

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

