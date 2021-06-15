---
title: 【Day 2】关于我是如何干掉Appium和RobotFramework这件事的——iOS自动化
date: 2021-06-14 14:00:00 +/-TTTT
categories: [客户端自动化,框架设计]
tags: [python,自动化,iOS,Android,Appium]
typora-copy-images-to: ../assets/img
typora-root-url: ../../vancheung.github.io
---




​	提到iOS自动化，必然绕不开的一个工具就是WebDriverAgent（后文简称 WDA），后续iOS自动化的设计也将围绕WDA进行。

### 什么是WDA

​	WebDriverAgent是Facebook制作的一款开源移动测试框架，支持真机和模拟器，官方Readme的介绍如下：

>   WebDriverAgent 在 iOS 端实现了一个 [WebDriver server](https://w3c.github.io/webdriver/webdriver-spec.html) ，借助这个 server 我们可以远程控制 iOS 设备。你可以启动、杀死应用，点击、滚动视图，或者确定页面展示是否正确。它是 iOS 上一个完美的 e2e 的自动化解决方案，链接`XCTest.framework`调用苹果的 API 直接在设备上执行命令。

​	虽然Facebook目前已经停止维护WDA，但其作为Appium在iOS平台自动化测试方案的核心，仍然是一个主流的iOS自动化方案。本框架在设备侧采用Appium fork的wda分支 [appium wda](https://github.com/appium/WebDriverAgent) ，在控制侧使用openatx框架的 [facebook-wda](https://github.com/openatx/facebook-wda) 。

​	简单介绍下WDA原理，WebDriverAgent作为一个xcporject，在Mac OS执行编译，会将一个WebDriverAgentRunner应用部署到被测设备上，同时在设备上开启一个监听端口，监听HTTP请求。使用任意一个可以发送HTTP请求的语言，都可以和设备上的WebDriverAgentRunner进行通信。WebDriverAgentRunner通过调用iOS提供的XCTest和Accessibility API进行自动化。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=NzJmNTgxYjYwZjk5MmFjODYxNzllOGJlM2MzMTU1Y2ZfMEg3alFvRUlscm03aUtsNVJzeWxpemJWWDZXc200TTJfVG9rZW46Ym94Y25tc25BVU1Gdm9UZ0RjWEhITzd3cWhnXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

（图源TesterHome）

​	对应我们的操作，也可以分为两个部分：编译WDA、使用python与WDA通信。

### 使用python-wda进行iOS UI自动化

#### 编译wda

​	首先，需要准备Mac OS的设备，git clone [WebDriverAgent](https://github.com/appium/WebDriverAgent) 到本地路径下。

```bash
git clone https://github.com/appium/WebDriverAgent.git  # 下载WDA代码

cd WebDriverAgent/ # 进入路径下

brew install carthage # 如果未安装过carthage的话需要先安装

./Scripts/bootstrap.sh  # 启动WDA必须的步骤
```

​	构建WDA可以通过Xcode界面操作或通过`xcodebuild`命令行，建议先通过界面构建，测试无问题后，后续使用命令行在测试脚本中进行构建。

​	使用Xcode打开WDA项目，File-Open-对应目录下选择WebDriverAgent.xcodeproj，或使用命令行：

```bash
cd WebDriverAgent/ # 进入路径下

open WebDriverAgent.xcodeproj
```

​	打开项目后修改Scheme为WebDriverAgentRunner：

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTVhZmMwYmZmODlmMmE5M2U1MDZmZjY1ODY1OTE0N2JfMlJ6Uk05Z0Z3MFAwYldHcXJnZGh4eVE4RVY2VnZWa0hfVG9rZW46Ym94Y25jblhmUTN2bXBFaDh6cnZaQU5pcTVnXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	虚拟机编译不需要有效的Apple账户，直接选择一个已安装的虚拟机，Product-Test即可。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=YTg2YjVhZWQwNmZhZjIxY2I2Yzc2YjBhNzliNDJjMjJfc0tiN1A4NW9RakU3TjhCQ2d0UmhhbnBsc3JDUG50bVZfVG9rZW46Ym94Y25HSXA5Y1pjMmI2MnZheXBvcE4zdkxoXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	编译成功后会启动一个URL，对于虚拟机来说，IP为Mac的IP，PORT在此文件中被指定，默认为8100。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=MGViNGMwYjAxNmNkMGE2MDczMjQwN2U2MTNjNWFlNjRfVVk1ZUI2UkNNWWxWaWQyZUtyT3RTY1lVRVBtU2RPbkpfVG9rZW46Ym94Y251N0c3QU5KTDJ6YkxMMHlINGhtcExnXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	在通过命令行构建时可以使用USE_PORT字段来指定此模拟器对应的WDARunner端口。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=NjBjNWQ3YjMxMWJiNWNlZjQ0MTNlNWJkYjc2NDIwZGJfbGUxd1BDQkdlQ3NuSVBMVGtTZVBWQ2I3UGw3RUt3eFhfVG9rZW46Ym94Y25mNzNHcEM5TXF5b1pNcnRpMEZvMTFnXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	控制台能打印如下内容，且在浏览器中访问 [http://localhost:8100/](https://link.zhihu.com/?target=http://localhost:8100/) （8100需要改为实际使用的端口）能够正常打印Json内容，即为启动成功。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=ZTJkOGQxMjc1ODRiOTU4NThjNWMzODQyNjlkMjExNDhfQVhpeXRNc2xIRGJvVEZQTVZqNTN3bVJjZkUwNUl3dXhfVG9rZW46Ym94Y25NNkZFeHkyd21YMzRCTVdJandUOXlkXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	真机编译需要准备一个苹果开发者账户，免费账户有设备数和编译项目数的限制，最好是准备个人开发者账户。

​	首先，修改Product Bundle Identifier为自定义的且唯一的Bundle ID，不能与Apple已记录的项目重复。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=NjIzODQ1NTlkMThjYTg3NzViMGNlYzA2OTdlOWI2OTJfRHN6UDc1QTY0alJYOTNKb3lMdXkyRkxlYzFTNkREM2xfVG9rZW46Ym94Y25INzNHNGFpR1hPNjRJUGVhRmZzREJoXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	修改Sign & Capabilities，选择Add Account

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=NWU2MDFlMjdiOTIxODEyMzNjYmQ4YzRjYTVmOGRlOWFfZFozeVZqOEFZZHpEdjdzTVNXdk02WjZETUduMlZMbkdfVG9rZW46Ym94Y253d2lZQWptVW5YVGtJZk0zQkFEZXhiXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	登录自己的开发者账户

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=MmMyZGRmY2ExZWIwYTIzOTY2YmI5Y2JmZmE3Nzg2YWZfTmNqaVQ5aFJ3YmhOQ0VVNFlUZk10NjBQNzlTdXB5V1hfVG9rZW46Ym94Y253YzVLZWhjdXFSa2NFc0F3ZHFocTFjXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

​	回到Sign & Capabilities，选择已登录的账户，无报错即可编译，后续操作与模拟器编译相同。

![img](https://mt7z4ki33y.feishu.cn/space/api/box/stream/download/asynccode/?code=ZDUyNGJiZjg4NzQxNWIxMjQ5MDVlN2E5MGU1M2RiMDdfQ3VkTnB2NlB2UFJLU0VZWVVQQ1dOcktJZWNzWUw2Mm9fVG9rZW46Ym94Y24yb3p5OURhc3VCM0lXYUE2bDY0eWVnXzE2MjM3NDQ4OTg6MTYyMzc0ODQ5OF9WNA)

#### 使用python-wda

​	python-wda是openatx框架提供的库，基于纯python方式发送HTTP请求，与客户端上的WebDriver进行交互。可以使用pip install安装python-wda。

```bash
pip install facebook-wda
```

​	一些简单的操作示例：

```python
import wda

# 初始化
wda_port = 8100
wda_client = wda.Client('http://localhost:%s' % self.wda_port)

# 处理系统弹窗
wda_client.alert.accept()

# 获取当前界面所有元素
elems = wda_client.source() 

# 通过元素的某个属性（如name）查找元素（返回Selector）
sel = wda_client(name='xxx')

# 通过元素的某个属性（如name）查找元素（返回Element）
ele = wda_client(name='xxx').get(timeout=5.0)

# 点击
ele.click()
```

### 命令行控制真机和虚拟机

一些命令无法通过wda实现，只能使用Apple提供的命令进行操作，因此作为一个utils引入项目。

代码见此文件：[xcmd.py](https://github.com/Vancheung/ClientEngine/blob/master/Engine/utils/xcmd.py)

其中，XDevice和XSimulator分别对应真机和模拟器的操作。

### submodule引入

引入python-wda作为移动端UI自动化框架，在此使用fork库中的url，方便后续更改。

引入操作：

```bash
# github 添加子模块
cd Engine/lib
git submodule add -f https://github.com/Vancheung/facebook-wda.git wda
```

在clone ClientEngine代码时同步子仓代码：

```bash
git clone --recursive https://github.com/Vancheung/ClientEngine.git
```

### 总结

目前的UI自动化工具，还是很难绕开WDA。据了解有一些大厂会做一些基于Framework注入的工具，提供一些诸如OC反射调用UI方法的能力。但这些工具的制作和维护需要OC/Swift相关能力，一般的测开同学难以自己实现。希望这些工具也能像Facebook WDA一样，有朝一日在开源社区见到它们的踪影。