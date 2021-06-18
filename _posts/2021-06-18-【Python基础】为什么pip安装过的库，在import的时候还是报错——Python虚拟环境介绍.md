---
title: 【Python基础】为什么pip安装过的库，在import的时候还是报错——Python虚拟环境介绍
date: 2021-06-18 14:00:00 +/-TTTT
categories: [Python编程,Python基础]
tags: [python,pip,venv,旧文搬运]
typora-copy-images-to: ../assets/img
---

### 【问题描述】 

最近收到一些同事们的疑问，为什么使用pip安装后的库，在PyCharm导入的时候还是会报 ModuleNotFoundError: No module named 'xxx'

![image-20210617105252572](/assets/img/image-20210617105252572.png)

如果只想简单粗暴的解决问题，以下方法二选一：

（1）在当前项目下打开Terminal窗口，重新pip安装一次对应的库

![image-20210617110029015](/assets/img/image-20210617110029015.png)

（2）在Preferences中修改当前项目的Python Interpreter为系统的python路径

![image-20210617105442390](/assets/img/image-20210617105442390.png)

但知其然在此处，还是总结一下为什么会出现这种问题，以及如何选择更合适自己的解决方法。

### 【原理详解】

#### 1、解释器（Interpreter）

Python是一门解释型语言，不需要编译和链接，代码在运行时通过解释器来翻译成机器语言执行。

因此，从cmd或Terminal窗口输入python（已配置环境变量）、运行可执行文件python（如python.exe）、或在PyCharm中打开Python Console，这三个操作本质都是运行了一个可执行程序python.exe，即Python的解释器。



解释器运行的时候有点像 Unix 命令行：在一个标准输入 tty 设备上调用，它能交互式地读取和执行命令；调用时提供文件名参数，或者有个文件重定向到标准输入的话，它就会读取和执行文件中的 *脚本*。 （来自Python官方文档：<https://docs.python.org/zh-cn/3/tutorial/interpreter.html> ）

即，Python的解释器有两种运行模式，*交互模式*，和*脚本执行模式*。

当解释器运行在交互模式下时（如上图所示），我们可以在解释器中方便地运行一些代码和计算，不需要写一个完整的.py文件

![image-20210617110741319](/assets/img/image-20210617110741319.png)

当解释器运行在脚本执行模式时，需要在启动解释器时指定脚本的路径和文件名，即

```python
python xxx.py
```

此时解释器会运行该文件的__main__函数。

![image-20210617143743975](/assets/img/image-20210617143743975.png)

![image-20210617143730559](/assets/img/image-20210617143730559.png)

#### 2、虚拟环境（virtual environment）

Python应用程序通常会使用不在标准库内的软件包和模块。应用程序有时需要特定版本的库，因为应用程序可能需要修复特定的错误，或者可以使用库的过时版本的接口编写应用程序。

这意味着一个Python安装可能无法满足每个应用程序的要求。如果应用程序A需要特定模块的1.0版本但应用程序B需要2.0版本，则需求存在冲突，安装版本1.0或2.0将导致某一个应用程序无法运行。（来自Python官方文档：<https://docs.python.org/zh-cn/3/tutorial/venv.html> ）

就是说，同一台开发机上可能会有多个Python项目，基于版本不同的软件包（第三方库）开发，为了避免出现版本冲突，让这些项目可以正常运行，Python使用了virtual environment作为解决方案，即：

创建一个虚拟环境，将Python解释器、标准库加入这个虚拟环境，在虚拟环境中安装其他软件包。

使用虚拟环境的优点在于：

1、系统中可以共存python2、python3版本，根据具体项目选择合适的版本

2、缩减包的数量，避免引入一些本项目中无关的包

3、同一个包，可以在不同项目中使用不同版本，不会产生冲突

但也会引入一些问题，比如：

1、增加操作复杂度，对初学者不友好，会引发本文开篇的疑问

2、可能会在每个虚拟环境中重复引用一些相同的包，占用本地空间

权衡一下优劣，还是更推荐使用虚拟环境开发的方式，另外，合理使用PyCharm可以简化很多操作。

#### 3、源问题根因

在Windows系统中，一般会把Python环境变量配置为Python默认安装目录，即：在命令行启动python/调用pip的时候，会启动安装目录下的python.exe。

如果通过pip安装的库与项目运行环境不是同一个解释器，就会出现该问题。

即：安装在系统目录，在当前项目的虚拟环境执行；或安装在当前虚拟环境，在系统目录或其他虚拟环境中使用。

### 【PyCharm中的虚拟环境】

根据Python官方文档，用命令行配置虚拟环境操作相对复杂，推荐直接使用PyCharm创建和管理虚拟环境

#### 1、使用虚拟环境

##### a.创建项目时创建新的虚拟环境

PyCharm在新建项目时，一些版本默认推荐的是随项目创建一个新的虚拟环境

![image-20210617144339089](/assets/img/image-20210617144339089.png)

或可以在选择解释器的时候Create VirtualEnv

![image-20210617144529160](/assets/img/image-20210617144529160.png)

配置虚拟环境的名称和路径，选择Base interpreter（Python2或Python3）

![image-20210617144540954](/../../../Users/admin/Documents/zxf/vancheung.github.io/assets/img/image-20210617144540954.png)

PyCharm中默认虚拟环境仅在当前项目中可用，如果有多个项目使用了相同的包，可以将虚拟环境配置为其他项目可见，勾选Make available to all projects。

![image-20210617144559354](/assets/img/image-20210617144559354.png)

点击OK，完成创建虚拟环境后，就可以指定本项目使用哪个虚拟环境

![image-20210617144700503](/assets/img/image-20210617144700503.png)

##### b.在项目中查看当前使用的解释器

在PyCharm中，Terminal窗口看到的路径如果前面有括号，说明当前解释器用的是虚拟环境中的，具体的虚拟环境名就是括号中的内容，如'venv'

![image-20210618114905606](/assets/img/image-20210618114905606.png)

打开Python Console，会显示当前虚拟环境的解释器地址

![image-20210618114954235](/assets/img/image-20210618114954235.png)

在PyCharm中run当前文件，也可以看到实际上PyCharm会调用虚拟环境里的python.exe执行

![image-20210618115019079](/assets/img/image-20210618115019079.png)

##### c.管理虚拟环境

打开Settings，查看Project Interpreter，可以看到当前虚拟环境中有哪些包

![image-20210618115047424](/assets/img/image-20210618115047424.png)

在下来菜单中可以选择修改当前项目的解释器，使用其他虚拟环境或系统默认环境

![image-20210618115110652](/assets/img/image-20210618115110652.png)

##### d.在项目中使用系统默认环境

在设置中修改解释器

![image-20210618115136482](/assets/img/image-20210618115136482.png)

修改后重新打开Terminal、Python Console、Run，可以看到项目使用的解释器都发生了变化

![image-20210618143422829](/assets/img/image-20210618143422829.png)

![image-20210618143445809](/assets/img/image-20210618143445809.png)

![image-20210618143304727](/assets/img/image-20210618143304727.png)

#### 2、使用requirements

Python包管理中，一种常见的做法是将本package引用的所有包，导出到一个requirements.txt文件，在新项目中使用本package时，可以通过pip requirements.txt一次性安装所有需要的包。

具体操作如下：

在Terminal中执行导出

`pip freeze > requirements.txt`

在新项目Terminal中执行导入

`pip install -r requirements.txt`