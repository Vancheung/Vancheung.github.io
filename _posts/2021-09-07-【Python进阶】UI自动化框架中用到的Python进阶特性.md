---
title:【Python进阶】UI自动化框架中用到的Python进阶特性
date: 2021-09-07 14:00:00 +/-TTTT
categories: [Python编程,Python基础]
tags: [python,旧文搬运]
typora-copy-images-to: ../assets/img
---


## 一、抽象类

在实现UI自动化框架时，存在一个常见的情况，Android和iOS封装相同的接口，从而实现用例的一致性，如下是一个简单的示例：

```python
class AndroidClient:
    def open_app(self):
        # some code
        
class IosClient:
    def open_app(self):
        # some code

if __name__ == "__main__":
    if platform=="android":
        client = AndroidClient()
    else:
        client = IosClient()
    client.open_app()
```

下文根据这两个示例类进行讲解。

### 1、继承

当AndroidClient和IosClient之间存在相同的操作时，为了减少代码重复，可以通过类的继承来实现。定义一个共同的父类BaseClient，将公共的操作在父类中实现。

```python
class BaseClient:
    def install(self):
        # some code

class AndroidClient(BaseClient):
    # some code
        
class IosClient(BaseClient):
    # some code

# 子类可以直接调用父类的方法
# client = AndroidClient() or client = IosClient()
client.install()
```

### 2、抽象类

按照上面的写法，BaseClient类也可以实例化：`client = BaseClient()`

现实中，并不存在BaseClient，被测设备类型只能为iOS或Android其中之一。

因此，BaseClient不应该直接被实例化。在Python中可以通过[抽象类](https://python3-cookbook.readthedocs.io/zh_CN/latest/c08/p12_define_interface_or_abstract_base_class.html)来实现这一特性。

```python
from abc import ABCMeta

class BaseClient:
    __metaclass__ = ABCMeta
    
    def install(self):
        # some code

client = BaseClient()
# TypeError: Can't instantiate abstract class
```

在抽象类中，有一些方法需要在子类中具体实现，但是需要在父类中定义接口，这样的情况可以用**抽象方法(abstractmethod)**来实现。

```python
from abc import ABCMeta, abstractmethod

class BaseClient:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def open_app(self):
        raise NotImplementedError # 或pass也可以

class AndroidClient:
    def open_app(self):
        # some code
        
class IosClient:
    def open_app(self):
        # some code
```

## 二、单例类

UI自动化框架中一些资源管理类（如：设备管理）在整个执行过程中，只需要实例化一次，否则可能会引起资源冲突。因此可以将这些类定义为单例类。

单例类有多种实现方式，在此只举例一种：通过重载类的`__new__`方法实现单例。

```python
class DeviceMgr:
    def __init__(self, name, udid):
        self.name = name
        self.udid = udid

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(DeviceMgr, cls).__new__(cls)
        return cls.instance
```

当我们实例化一个对象时，Python解释器会先执行了类的`__new__`方法（没写时，默认调用`object.__new__`）来实例化对象，然后再执行类的`__init__`方法，对这个对象进行初始化。

基于这个特性，在实现单例模式的时候，可以在类的`__new__`方法中增加一个**instance**属性，如果查到了**instance**则直接返回，否则调用类的`__new__`方法来实例化对象。

可以在Python Console中看一下单例类与非单例类的区别

```python
# 普通类
>>> class A:
>>>     pass
>>> a = A()
>>> id(a) # 查看对象的内存地址
4511753600
>>> b = A()
>>> id(b) # b与a的内存地址不一样，说明对应到不同的实例
4495172368

# 单例类
>>> class A:
>>>     def __new__(cls, *args, **kwargs):
...         if not hasattr(cls, "instance"):
...             cls.instance = super(A, cls).__new__(cls)
...         return cls.instance
    
>>> a = A()
>>> id(a)
4512506832
>>> b = A()
>>> id(b)  # b与a的内存地址一样，说明对应到同一个实例
4512506832
```

## 三、类的字典

在Python中，类的属性是通过字典来管理的，可以通过调用`__dict__`来查看实例的属性。

```python
>>> class A:
    def __init__(self):
        self.name='a'
        self.udid='123456'
        
>>> a = A()
>>> a.__dict__
{'name': 'a', 'udid': '123456'}
```

对于一些类（如设备信息），不同的设备类型传入的字段不一致，而在其他地方又想通过"`类.属性`"的方式来调用这些属性，可以通过设置`__dict__`来实现。

```python
>>> class DeviceInfo:
...     def __init__(self, **entries):
...         self.__dict__.update(entries)

>>> device_1 = {
...     "udid": "123456",
...     "wdaUrl": "10.1.1.1"
... }
>>> d1 = DeviceInfo(**device_1)
>>> d1.udid
'123456'
>>> d1.wdaUrl
'10.1.1.1'

>>> device_2 = {
...     "udid": "456789",
...     "atxAgentAddress": "10.2.2.2"
... }
>>> d2 = DeviceInfo(**device_2)
>>> d2.atxAgentAddress
'10.2.2.2'

```

## 四、python的反射调用

在Python中存在动态调用一些方法的场景，例如，我们通过Page类管理页面元素信息，而Page类中具体页面的内容，是在代码运行时才设置的。

这种情况下，可以通过**setattr**来动态设置类的属性，通过**getattr**和字符串反射调用对象。

```python
class Page:
    def load_page(self):
        # 一些加载页面的动作
        # page_name, page_value = self.load()
        setattr(self, page_name, page_value)

page = Page()

# 使用非反射的逻辑
if page.主页:
    # some code
elif page.页面1:
    # some code
elif page.页面2:
    # some code

# 使用反射的逻辑
tab_names = ["主页","页面1","页面2"]
for tab in tab_names:
    test_page = getattr(page, tab)
    # test_page.xxx操作
```

采用反射可以减少if-else逻辑判断，让代码更简洁。

另一个典型的使用反射的例子，是Web框架中的路由功能。

```python
# 不使用反射，需要逐一判断
def deal_route():
    page = input("请输入您想访问页面的url：").strip().split('/')[-1]
    if page == "login":
        commons.login()
    elif page == "logout":
        commons.logout()
    elif page == "home":
        commons.home()
    else:
        print("404")

# 使用反射，无需判断，直接通过字符串调用
def deal_route():
    page = input("请输入您想访问页面的url：").strip().split('/')[-1]
    if hasattr(commons,page):
        func = getattr(commons,page)
        func()
```

## 五、函数式编程

函数式编程是一种编程范式，将计算机运算视为函数运算，并且避免使用程序状态及易变对象。

**函数式编程的特征**

-   **stateless**：函数不维护任何状态。
-   **immutable**：输入数据发生变化时，返回新的数据集。
-   **惰性求值**：表达式不在它被绑定到变量之后就立即求值，而是在该值被取用的时候求值。
-   **确定性**：所谓确定性，就是像在数学中那样，`f(x) = y` 这个函数无论在什么场景下，都会得到同样的结果。

应用函数式编程，函数之间没有共享的变量，而是通过参数和返回值传递数据，可以重点关注做什么而非怎么做。

根据 **Algorithm = Logic +Control** ，在Python中使用map、reduce、filter，实际上改变的是 Control 的部分，即改变算法执行的策略，而不修改真正的业务Logic。

### 0. lambda

Python中可以用 [`lambda`](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.python.org%2Fzh-cn%2F3%2Freference%2Fexpressions.html%23lambda) 关键字来创建一个小的**匿名函数**。

例如，这个lambda函数返回两个参数的和： `lambda a, b: a+b` 。

Lambda函数可以在需要函数对象的任何地方使用。在语法上，仅限于单个表达式。从语义上来说，它们只是正常函数定义的语法糖。

### 1. map

先看一个示例，下面的代码使用常规的面向过程方式，将一个字符串中所有小写字母转换为大写：

```python
lowname = ['hello','world']
upper_name =[] 
for i in range(len(lowname)):
    upper_name.append( lowname[i].upper() )
```

面向过程的写法通过一个循环读取所有输入，依次进行转换。

而函数式的写法，将转换过程抽象成一个函数，然后在调用时不需要使用循环，而是使用map关键字:

```python
def toUpper(item):
      return item.upper()
upper_name = map(toUpper, ['hello','world'])
```

在builtins.py文件中，可以查看map的定义：

```csharp
map(func, *iterables) --> map object

Make an iterator that computes the function using arguments from each of the iterables.  Stops when the shortest iterable is exhausted.
```

即，map将func函数应用于传入序列的每个元素，并将结果作为新的list返回。map抽象了运算规则，使代码更易阅读。

函数func可以为一个具体的函数，也可以为一个lambda函数，例如下面的代码会把nums列表中每一个数乘3。

```python
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] 
newnums = map(lambda x: x*3, nums)
```

func参数的类型是一个function对象，只需要写函数名，不需要加括号。

### 2. reduce

在Python3中，使用reduce需要先从functool中引入，在_functools.py中可以查看reduce函数的定义。

```python
reduce(function, sequence[, initial]) -> value

Apply a function of two arguments cumulatively to the items of a sequence,
from left to right, so as to reduce the sequence to a single value.
For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates ((((1+2)+3)+4)+5).  If initial is present, it is placed before the items of the sequence in the calculation, and serves as a default when the
sequence is empty.
```

reduce对在参数序列中的元素，执行函数function，这个函数必须接收两个参数，reduce把结果继续与序列的下一个元素进行累积计算。

再看一个简单的示例，对一个列表中所有元素求和，非函数式编程的写法如下：

```python
nums = [2, -5, 9, 7, -2, 5, 3, 1, 0, -3, 8]
result = 0
for i in nums:
    result += i
```

使用reduce，可以隐藏数组遍历求和控制流程，让代码的业务逻辑更清晰：

```python
from functools import reduce
nums = [2, -5, 9, 7, -2, 5, 3, 1, 0, -3, 8]
result = reduce(lambda x,y:x+y, nums)
```

当函数变复杂时，reduce的收益就会更明显，例如，将序列转换为整数：



```python
from functools import reduce
nums = [2, 5, 9, 7, 2, 5, 3, 1, 0, 3, 8]
result = reduce(lambda x,y:x*10+y, nums)
# result = 25972531038
```

### 3. filter

filter应用于过滤序列，以一个判断函数和可迭代对象作为参数，返回序列中满足判断函数的元素组成的列表。

```bash
filter(function or None, iterable) --> filter object

Return an iterator yielding those items of iterable for which function(item) is true. If function is None, return the items that are true.
```

例如，过滤出一个列表中所有奇数：

```python
def is_odd(n):
    return n % 2 == 1
newlist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
```

函数式编程三套件map、reduce、filter，都属于简化控制流程的函数。适当使用可以使代码更清晰易读，更聚焦于业务处理逻辑。例如，写一个计算数组中所有正数平均值的函数，使用面向过程的写法如下：

```python
# 计算数组中正数的平均值
num = [2, -5, 9, 7, -2, 5, 3, 1, 0, -3, 8]

def calcute_average(num):
    positive_num_cnt = 0
    positive_num_sum = 0
    average = 0
    for i in range(len(num)):
        if num[i] > 0:
            positive_num_cnt += 1
            positive_num_sum += num[i]

    if positive_num_cnt > 0:
        average = positive_num_sum / positive_num_cnt

    return average
```

而使用函数式编程写法如下：

```python
def calcute_average2(num):
    positive_num = list(filter(lambda x: x > 0, num)) # 过滤正数
    return reduce(lambda x, y: x + y, positive_num) / len(positive_num)  # average = 正数列表求和/正数个数
```

注意：python3中filter函数的返回值为一个filter对象，需要转换成list对象才能使用reduce，而python2中可以直接写

```
positive_num = filter(lambda x: x > 0, num)
```

可以看到，这种方法通过去掉循环体，解耦了控制逻辑与业务逻辑，去掉了控制逻辑中的临时变量，代码重点在描述“做什么”。

