---
title: 【Day 3】关于我是如何干掉Appium和RobotFramework这件事的——Android自动化
date: 2021-06-15 14:00:00 +/-TTTT
categories: [客户端自动化,框架设计]
tags: [python,自动化,iOS,Android,Appium]
typora-copy-images-to: ../assets/img
typora-root-url: ../../vancheung.github.io
---

### 什么是uiautomator2

​	摘抄一段来自[ uiautomator2](https://github.com/openatx/uiautomator2) 官方文档的介绍：

>   [UiAutomator](https://developer.android.com/training/testing/ui-automator.html)是Google提供的用来做安卓自动化测试的一个Java库，基于Accessibility服务。功能很强，可以对第三方App进行测试，获取屏幕上任意一个APP的任意一个控件属性，并对其进行任意操作，但有两个缺点：1. 测试脚本只能使用Java语言 2. 测试脚本要打包成jar或者apk包上传到设备上才能运行。

>   我们希望测试逻辑能够用Python编写，能够在电脑上运行的时候就控制手机。这里要非常感谢 Xiaocong He ([@xiaocong](https://github.com/xiaocong))，他将这个想法实现了出来（见[xiaocong/uiautomator](https://github.com/xiaocong/uiautomator)），原理是在手机上运行了一个http rpc服务，将uiautomator中的功能开放出来，然后再将这些http接口封装成Python库。 因为`xiaocong/uiautomator`这个库，已经很久不见更新。所以我们直接fork了一个版本，为了方便做区分我们就在后面加了个2 [openatx/uiautomator2](https://github.com/openatx/uiautomator2)

​	uiautomator2通过http协议与手机上的 [atx-agent](https://github.com/openatx/atx-agent)通信，atx-agent是一个Go语言编写的开源项目，它可以屏蔽不同安卓机器的差异，然后开放出统一的HTTP接口。项目最终会发布成一个二进制程序，运行在Android系统的后台。

​	之所以选择uiautomator2，是为了在多设备管理时，可以无缝集成[atxserver2](https://github.com/openatx/atxserver2)。

### 使用uiautomator2

​	运行atxserver2-android-provider之后会自动扫描已连接的Android设备，包括真机和模拟器，并在这些设备上部署atx-agent apk。uiautomator2.connect通过指定设备名称来建立连接。

#### pip安装uiautomator2

```bash
pip install uiautomator2
```

#### 初始化

查看已连接的设备名

```python
adb devices
# 初始化设备
import uiautomator2
u2_client = uiautomator2.connect(deviceName)
```

#### 安装应用

```python
# 安装应用
u2_client.app_install(app_path)
```

uiautomator2使用`adb push + pm`命令替代了 `adb install`，使其支持远程安装：

```python
self.push(data, target, show_progress=True)
self.shell(['pm', 'install', "-r", "-t", target])
```

​	当前版本存在一个问题，app_install默认超时时间是60s，超过60s会上报命令执行失败，实际安装成功。因此对源码进行修改，增加time_out字段，延长install操作等待时间.

```python
ret = self.shell(['pm', 'install', "-r", "-t", target],timeout=300)
```

https://github.com/Vancheung/uiautomator2/commit/578d73ec64546717abf8c6e7c993b03750d462ef

#### 处理弹窗

​	uiautomator2.device会单独启动一个watcher线程来检测弹窗，初始化watch_context的builtin=True之后，调用device.watcher.start()即可，默认的检查间隔时间为2s。调用device.watcher.stop()可关闭watcher线程。

此方法可供iOS借鉴。

```python
self.u2_client.watch_context(autostart=True, builtin=True)

def click_system_popup(self):
    self.u2_client.watcher.start()

def stop_click_system_popup(self):
    self.u2_client.watcher.stop()
```

WatchContext可以自己增加检测的关键词和操作，例如 https://github.com/Vancheung/uiautomator2/commit/e9f4e3087253b78119248f5239621caf24676793

```python
class WatchContext:
    def __init__(self, d: "uiautomator2.Device", builtin: bool = False):
        ……
        if builtin:
            self.when("继续使用").click()
            self.when("移入管控").when("取消").click()
            self.when("^立即(下载|更新)").when("取消").click()
            self.when("同意").click()
            self.when("^(好的|确定)").click()
            self.when("继续安装").click()
            self.when("安装").click()
            self.when("Agree").click()
            self.when("ALLOW").click()
```

#### 查找元素

​	与iOS类似，u2_client(**kwargs)会返回一个uiautomator._selector.UiObject对象，包含Session对象和Selector对象，而Selector支持如下字段：

```python
class Selector(dict):

    """The class is to build parameters for UiSelector passed to Android device.

    """
    __fields = {
        "text": (0x01, None),  # MASK_TEXT,
        "textContains": (0x02, None),  # MASK_TEXTCONTAINS,
        "textMatches": (0x04, None),  # MASK_TEXTMATCHES,
        "textStartsWith": (0x08, None),  # MASK_TEXTSTARTSWITH,
        "className": (0x10, None),  # MASK_CLASSNAME
        "classNameMatches": (0x20, None),  # MASK_CLASSNAMEMATCHES
        "description": (0x40, None),  # MASK_DESCRIPTION
        "descriptionContains": (0x80, None),  # MASK_DESCRIPTIONCONTAINS
        "descriptionMatches": (0x0100, None),  # MASK_DESCRIPTIONMATCHES
        "descriptionStartsWith": (0x0200, None),  # MASK_DESCRIPTIONSTARTSWITH
        "checkable": (0x0400, False),  # MASK_CHECKABLE
        "checked": (0x0800, False),  # MASK_CHECKED
        "clickable": (0x1000, False),  # MASK_CLICKABLE
        "longClickable": (0x2000, False),  # MASK_LONGCLICKABLE,
        "scrollable": (0x4000, False),  # MASK_SCROLLABLE,
        "enabled": (0x8000, False),  # MASK_ENABLED,
        "focusable": (0x010000, False),  # MASK_FOCUSABLE,
        "focused": (0x020000, False),  # MASK_FOCUSED,
        "selected": (0x040000, False),  # MASK_SELECTED,
        "packageName": (0x080000, None),  # MASK_PACKAGENAME,
        "packageNameMatches": (0x100000, None),  # MASK_PACKAGENAMEMATCHES,
        "resourceId": (0x200000, None),  # MASK_RESOURCEID,
        "resourceIdMatches": (0x400000, None),  # MASK_RESOURCEIDMATCHES,
        "index": (0x800000, 0),  # MASK_INDEX,
        "instance": (0x01000000, 0)  # MASK_INSTANCE,
    }
```

因此与wda不同的是，无需再调用get方法，就可以直接操作uiautomator._selector.UiObject对象的UI动作。因此查找元素的实现如下：

```python
ele = u2_client(name='xxx')
# 点击操作
ele.click()
```

### submodule引入

​	引入uiautomator2作为移动端UI自动化框架，在此使用fork库中的url，方便后续更改。

```bash
# github 添加子模块
cd Engine/lib
git submodule add -f https://github.com/Vancheung/uiautomator2.git uiautomator2
```

在clone ClientEngine代码时同步子仓代码：

```bash
git clone --recursive https://github.com/Vancheung/ClientEngine.git
```

### 总结

​	相较iOS而言，Android系统整体开放性更强，可用工具也比较多，不管是基于adb、HTTP还是socket、RPC，可供选择的比较多，导致工具选型也成为了一个问题。考虑到需要集成atxserver，暂时选用uiautomator2来做，这只能说是当前范围内的一个最优解，并不存在绝对意义上的最佳选择。