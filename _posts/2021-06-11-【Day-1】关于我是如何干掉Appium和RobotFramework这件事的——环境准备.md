---
title: 【Day 1】关于我是如何干掉Appium和RobotFramework这件事的——环境准备
date: 2021-06-11 10:00:00 +/-TTTT
categories: [客户端自动化,框架设计]
tags: [python,自动化,iOS,Android,Appium]
typora-copy-images-to: ../assets/img
typora-root-url: ../../vancheung.github.io
---

### 工具安装

虽说工欲善其事，必先利其器，但准备环境的文档在互联网上以多如牛毛，不再赘述。在此，只记录下需要准备的内容有哪些。

#### 一个好用的Python IDE

个人习惯使用PyCharm， VS Code也是不错的选择。

#### Xcode

​	在Mac上运行本工程，涉及iOS和Mac OS自动化，必须要安装Xcode。建议使用最新稳定版本，并更新全量iOS Support Files，更新方法：

```bash
git clone https://github.com/iGhibli/iOS-DeviceSupport.git

cd iOS-DeviceSupport/

sudo ./deploy.py
```

​	当iOS有新的系统版本时，`git pull` 这个项目，然后再次执行deploy即可。

​	如果你的手机不幸跟我一样是iOS 14.6版本，Apple没有提供14.6的DeviceSupport，可以直接到应用目录下复制一份14.5的目录即可

```bash
cd /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/DeviceSupport
cp -r 14.5 14.6
```

#### Android Studio

直接通过官网下载安装，并手动安装一个最常用的Aandroid SDK版本。

如果本机没有安装Java的话，建议安装openjdk8。

#### Mac运行脚本

我已将Mac安装场景常用的命令汇总为一个脚本：[env_install.sh](https://github.com/Vancheung/ClientEngine/blob/main/Engine/utils/env_install.sh) ，在Mac环境下直接 `sudo ./env_install.sh` 即可安装。在此感谢 https://github.com/i5ting/i5ting-mac-init 和 https://github.com/wizarot/laptop 两位贡献的内容。

```bash
#!/bin/bash
# 需要完成Xcode安装，并且将xcode移动到应用程序目录下，再运行此脚本

brew_is_installed() {
  brew list -1 | grep -Fqx "$1"
}

# 装brew同时会自动安装xcode command line tools 详见其官网: https://brew.sh/index_zh-cn

echo "-----------------------------------------------"
echo "安装brew以及xcode command line tools:"
if  [ ! command -v brew >/dev/null 2>&1 ]
then
	echo "安装homebrew..."
	# 官网推荐的brew安装方式:
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	# 另一种备用方式
	# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
	export SHELL="/bin/zsh"

	# TODO: 如果安装失败,退出脚本

else
	echo "已安装brew,自动跳过..."
fi

# 启用xcode的命令行开发工具
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
# 使用特定版本xcode时修改 Xcode.app字段， 例如使用Xcode 10，并手动更改应用程序下Xcode名称为 Xcode10
# 则 sudo xcode-select -switch /Applications/Xcode10.app/Contents/Developer


echo "-----------------------------------------------"
echo "brew安装zsh 和 oh_my_zsh:"

if [ $SHELL != "/bin/zsh" ]
then
	echo "brew安装zsh"

	brew install zsh zsh-completions zsh-autosuggestions zsh-syntax-highlighting

	if ! grep "source /usr/local/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ~/.zshrc;
	then
		echo "source /usr/local/share/zsh-autosuggestions/zsh-autosuggestions.zsh" >> ~/.zshrc
	fi

	if ! grep "source /usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ~/.zshrc;
	then
		echo "source /usr/local/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ~/.zshrc
	fi

	echo "切换到zsh为默认shell"
	chsh -s $(which zsh)

	echo "安装oh_my_zsh，第一次执行完会跳出脚本，再次运行即可"
	sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

else
	echo "已经安装好zsh 和 oh_my_zsh,自动跳过..."
fi



echo "-----------------------------------------------"
echo "安裝git:"
git --version
if  [ `echo $?` -ne 0 ]
then
	brew install git
else
	echo "git 安装完成!"
fi

echo "-----------------------------------------------"
echo "安装brew cask"
brew tap homebrew/cask
brew tap homebrew/cask-versions

echo "-----------------------------------------------"
echo "brew安装自动化测试所需组件"
# 遍历更新
for app in libimobiledevice ideviceinstaller carthage allure
do
echo "try to install " ${app}
brew install $app
done

# 安装appium （可选）
#echo "-----------------------------------------------"
#echo "node安装自动化测试所需组件"
#echo "安装nvm（node version manager）"
#curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.6/install.sh | bash
#echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
#echo '[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" # This loads nvm' >> ~/.zshrc
#source ~/.zshrc
#
#echo "-----------------------------------------------"
#echo "安装node"
#nvm install stable
#nvm alias default node
#echo "-----------------------------------------------"
#echo "安装自动化组件&appium"
#appium-doctor
#if  [ `echo $?` -ne 0 ]
#then
#	npm install ios-deploy -g
#	npm install appium -g
#	npm install appium-doctor -g
#else
#	echo "appium 安装完成!"
#fi
#
#
#echo "-----------------------------------------------"
#echo "appium-doctor"
#appium-doctor

echo "-----------------------------------------------"
echo "安装Java环境（可选）"
java -version
if  [ `echo $?` -ne 0 ]
then
	# 安装openjdk8
	brew install openjdk@8
	sudo ln -sfn /usr/local/opt/openjdk@8/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-8.jdk
	# 安装openjdk11 可选
	# wget https://download.java.net/java/GA/jdk11/13/GPL/openjdk-11.0.1_osx-x64_bin.tar.gz
	# sudo tar -zxf  openjdk-11.0.1_osx-x64_bin.tar.gz -C /Library/Java/JavaVirtualMachines/
	echo "配置Java环境变量JAVA_HOME"
	# echo 'export JAVA_11_HOME=$(/usr/libexec/java_home -v11)' >> ~/.zshrc
	# alias java11='export JAVA_HOME=$JAVA_11_HOME' >> ~/.zshrc
	echo 'export JAVA_8_HOME=$(/usr/libexec/java_home -v1.8)' >> ~/.zshrc
	echo 'export JAVA_HOME=$JAVA_HOME_8' >> ~/.zshrc

	source ~/.zshrc
else
	echo "java 安装完成!"
fi


echo "-----------------------------------------------"
echo "安装Android环境，需要提前手动下载Android Studio，并选择安装SDK: API Level 28（可选）"
adb --version
if  [ `echo $?` -ne 0 ]
then
	echo 'export ANDROID_HOME=~/Library/Android/sdk' >> ~/.zshrc
	echo 'export PATH=$PATH:$ANDROID_HOME/emulator' >> ~/.zshrc
	echo 'export PATH=$PATH:$ANDROID_HOME/tools' >> ~/.zshrc
	echo 'export PATH=$PATH:$ANDROID_HOME/tools/bin' >> ~/.zshrc
	echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.zshrc
	source ~/.zshrc
else
	echo "android sdk安装完成!"
fi

echo "脚本运行结束，请手动检查是否存在报错信息。如存在，请在解决Error问题后重新运行此脚本。"

```



### 日志模块

logger是最常用的功能之一，与其他内容无耦合关系。在此先实现一个基础的logger模块，供后续使用。 默认debug级别设置为：

```python
file_level = logging.DEBUG

console_level = logging.INFO
```

代码详见： https://github.com/Vancheung/ClientEngine/blob/main/Engine/utils/log_util.py

```python
# -*- coding: UTF-8 -*-

""" 自定义日志logger """

__LogPathName__ = "Report/Log"

import logging
import os
from datetime import datetime

from Engine import BASE_DIR

CUE_FILE_LOG = 'CueFileLog'
CUE_CONSOLE_LOG = 'CueConsoleLog'


class CueLog(object):
    ONLY_FILE = 1
    ONLY_CONSOLE = 2
    BOTH_FILE_CONSOLE = 3

    def __init__(self, **kwargs):
        """
        初始化日志对象。
        日志对象为单例，在初始化时可以对file_level、console_level设置不同的日志级别。
        Parameters
        ----------
        kwargs:
            file_level = logging.DEBUG
            console_level = logging.INFO
        """
        self.log_path = os.path.join(BASE_DIR, __LogPathName__)

        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        self._file_level = kwargs.get("file_level") if kwargs.get("file_level") else logging.DEBUG
        self._console_level = kwargs.get("console_level") if kwargs.get("console_level") else logging.INFO

        self.file_logger = logging.getLogger(CUE_FILE_LOG)
        self.console_logger = logging.getLogger(CUE_CONSOLE_LOG)
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.set_log_handler(self.file_logger, self._file_level)
        self.set_log_handler(self.console_logger, self._file_level)

    def set_log_handler(self, log_type, log_level):
        log_type.setLevel(log_level)
        self.file_logger.propagate = False
        if log_type.name == CUE_FILE_LOG:
            file_name = 'ClientTest_' + datetime.now().strftime('%Y%m%d') + '.log'
            file_path = os.path.join(self.log_path, file_name)
            handler = logging.FileHandler(file_path)
        else:
            handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(self.formatter)
        log_type.addHandler(handler)

    def __new__(cls):
        """
        单例
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(CueLog, cls).__new__(cls)
        return cls.instance

    @staticmethod
    def make_log_msg(title, **kwargs):
        msg = ''
        if len(kwargs) > 0:
            msg = ':'
            for k, v in kwargs.items():
                msg += ' {0}={1};'.format(k, v)
        return title + msg

    def format_msg(self, msg):
        rv = self.find_call_stack()
        if isinstance(msg, bytes):
            msg = msg.decode()
        if (rv is not None) and (len(rv) > 0):
            filepath = rv[0]
            [_, filename] = os.path.split(filepath)
            return "[{}] {}:{}: ".format(filename, rv[2], rv[1]) + msg
        else:
            return msg

    def warning2(self, flag, msg, *args, **kwargs):
        if self._file_level <= logging.WARNING or self._console_level <= logging.WARNING:
            msg = self.format_msg(msg)
        if (self._file_level <= logging.WARNING) and ((flag & self.ONLY_FILE) != 0):
            self.file_logger.warning(msg, *args, **kwargs)
        if (self._console_level <= logging.WARNING) and ((flag & self.ONLY_CONSOLE) != 0):
            self.console_logger.warning(msg, *args, **kwargs)

    def error2(self, flag, msg, *args, **kwargs):
        if self._file_level <= logging.ERROR or self._console_level <= logging.ERROR:
            msg = self.format_msg(msg)
        if (self._file_level <= logging.ERROR) and ((flag & self.ONLY_FILE) != 0):
            self.file_logger.error(msg, *args, **kwargs)
        if (self._console_level <= logging.ERROR) and ((flag & self.ONLY_CONSOLE) != 0):
            self.console_logger.error(msg, *args, **kwargs)

    def debug2(self, flag, msg, *args, **kwargs):
        if self._file_level <= logging.DEBUG or self._console_level <= logging.DEBUG:
            msg = self.format_msg(msg)
        if (self._file_level <= logging.DEBUG) and ((flag & self.ONLY_FILE) != 0):
            self.file_logger.debug(msg, *args, **kwargs)
        if (self._console_level <= logging.DEBUG) and ((flag & self.ONLY_CONSOLE) != 0):
            self.console_logger.debug(msg, *args, **kwargs)

    def info2(self, flag, msg, *args, **kwargs):
        if self._file_level <= logging.INFO or self._console_level <= logging.INFO:
            msg = self.format_msg(msg)
        if (self._file_level <= logging.INFO) and ((flag & self.ONLY_FILE) != 0):
            self.file_logger.info(msg, *args, **kwargs)
        if (self._console_level <= logging.INFO) and ((flag & self.ONLY_CONSOLE) != 0):
            self.console_logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.warning2(self.BOTH_FILE_CONSOLE, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.error2(self.BOTH_FILE_CONSOLE, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.debug2(self.BOTH_FILE_CONSOLE, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.info2(self.BOTH_FILE_CONSOLE, msg, *args, **kwargs)

    @staticmethod
    def find_call_stack():
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = logging.currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (co.co_filename, f.f_lineno, co.co_name)
            break
        return rv


logger = CueLog()
_srcfile = os.path.normcase(logger.error.__code__.co_filename)
```



### 总结

今日内容没什么技术含量，主要是费时间。