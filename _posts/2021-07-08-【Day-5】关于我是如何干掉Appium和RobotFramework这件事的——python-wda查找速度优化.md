---
title: 【Day 5】关于我是如何干掉Appium和RobotFramework这件事的——python-wda查找速度优化
date: 2021-07-08 18:00:00 +/-TTTT
categories: [客户端自动化,框架设计]
tags: [python,自动化,iOS,Android,Appium]
typora-copy-images-to: ../assets/img
typora-root-url: ../../vancheung.github.io
---

### 一、一次定位操作背后发生了什么

```python
# 初始化wda_client
import wda
wda_client = wda.Client()

# 调用查找元素
self.wda_client(label='登录')
```

这个行为会调用BaseClient类的`__call__`方法，返回一个Selector对象

```python
class BaseClient(object)
    def __init__(self, url=None, _session_id=None):
         self.__timeout = 30.0
         
    def __call__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.__timeout
        return Selector(self, *args, **kwargs)
```

而Selector对象在初始化的时候，接受如下参数：

```python
class Selector(object):
    def __init__(self,
                 session: Session,
                 predicate=None,
                 id=None,
                 className=None,
                 type=None,
                 name=None,
                 nameContains=None,
                 nameMatches=None,
                 text=None,
                 textContains=None,
                 textMatches=None,
                 value=None,
                 valueContains=None,
                 label=None,
                 labelContains=None,
                 visible=None,
                 enabled=None,
                 classChain=None,
                 xpath=None,
                 parent_class_chains=[],
                 timeout=10.0,
                 index=0):
```

此时并不会发生查找动作，即不会与wda进行交互。真正的查找发生在Selector.find_element_ids()方法被调用的时候，具体为以下场景：

```python
s = self.wda_client(label='登录')
s.get()
s.count()
s.exists

class Selector(object):
    def count(self):
        return len(self.find_element_ids())

    def exists(self):
        return len(self.find_element_ids()) > self._index

    def find_elements(self):
        """
        Returns:
            Element (list): all the elements
        """
        es = []
        for element_id in self.find_element_ids():
            e = Element(self._session, element_id)
            es.append(e)
        return es
    
    def get(self, timeout=None, raise_error=True):
        """
        Args:
            timeout (float): timeout for query element, unit seconds
                Default 10s
            raise_error (bool): whether to raise error if element not found
    
        Returns:
            Element: UI Element   

        Raises:
            WDAElementNotFoundError if raise_error is True else None
        """
        start_time = time.time()
        if timeout is None:
            timeout = self._timeout
        while True:
            elems = self.find_elements()
            if len(elems) > 0:
                return elems[0]
            if start_time + timeout < time.time():
                break
            time.sleep(0.5)
    
        if raise_error:
            raise WDAElementNotFoundError("element not found",
                                          "timeout %.1f" % timeout)
```

而find_element_ids()方法的实现如下：

```python
class Selector(object):
    @retry.retry(WDAStaleElementReferenceError, tries=3, delay=.5, jitter=.2)
    def find_element_ids(self):
        elems = []
        if self._id:
            return self._wdasearch('id', self._id)
        if self._predicate:
            return self._wdasearch('predicate string', self._predicate)
        if self._xpath:
            return self._wdasearch('xpath', self._xpath)
        if self._class_chain:
            return self._wdasearch('class chain', self._class_chain)
    
        chain = '**' + ''.join(
            self._parent_class_chains) + self._gen_class_chain()
        if DEBUG:
            print('CHAIN:', chain)
        return self._wdasearch('class chain', chain)       

    def _wdasearch(self, using, value):
        """
        Returns:
            element_ids (list(string)): example ['id1', 'id2']        
        HTTP example response:
        [
            {"ELEMENT": "E2FF5B2A-DBDF-4E67-9179-91609480D80A"},
            {"ELEMENT": "597B1A1E-70B9-4CBE-ACAD-40943B0A6034"}
        ]
        """
        element_ids = []
        for v in self.http.post('/elements', {
                'using': using,
                'value': value
        }).value:
            element_ids.append(v['ELEMENT'])
        return element_ids
```

find_element_ids会向wda发送http请求，查找/elements接口，并且失败自动重试三次。

![image-20210708182712250](/assets/img/image-20210708182712250.png)

而wda会使用using和value两个字段来共同定位XCUIElement元素。

![image-20210708182732092](/assets/img/image-20210708182732092.png)

using支持id、predicate string、xpath、class chain四种，其中我们常用label、name等，都是通过Selector._gen_class_chain方法拼接出来的。

```python
class Selector(object):
    def _gen_class_chain(self):
        # just return if aleady exists predicate
        if self._predicate:
            return '/XCUIElementTypeAny[`' + self._predicate + '`]'
        qs = []
        if self._name:
            qs.append("name == '%s'" % self._name)
        if self._name_part:
            qs.append("name CONTAINS %r" % self._name_part)
        if self._name_regex:
            qs.append("name MATCHES %r" % self._name_regex)
        if self._label:
            qs.append("label == '%s'" % self._label)
        if self._label_part:
            qs.append("label CONTAINS '%s'" % self._label_part)
        if self._value:
            qs.append("value == '%s'" % self._value)
        if self._value_part:
            qs.append("value CONTAINS '%s'" % self._value_part)
        if self._visible is not None:
            qs.append("visible == %s" % 'true' if self._visible else 'false')
        if self._enabled is not None:
            qs.append("enabled == %s" % 'true' if self._enabled else 'false')
        predicate = ' AND '.join(qs)
        chain = '/' + (self._class_name or 'XCUIElementTypeAny')
        if predicate:
            chain = chain + '[`' + predicate + '`]'
        if self._index:
            chain = chain + '[%d]' % self._index
        return chain
```

所以向wda发送请求时的body：

```html
POST /elements
{
    'using': 'class chain', 
    'value': "**/XCUIElementTypeAny[`label == '登录'`]"
}
```

而响应类似：

```html
{
    'ELEMENT': '20000000-0000-0000-B8C1-000000000000', 
    'element-6066-11e4-a52e-4f735466cecf': '20000000-0000-0000-B8C1-000000000000'
}
```

v['ELEMENT']可以认为是元素id，下次查询动作可以直接通过id来定位元素。

如果是调用Selector.find_elements获取元素id，会将取到的元素保存为一组Element对象。

```python
class Element(object):
    def __init__(self, session: Session, id: str):
        """
        base_url eg: http://localhost:8100/session/$SESSION_ID
        """
        self._session = session
        self._id = id
```

而查询Element对象的具体信息，需要调用Element的方法，如：

```python
class Element(object):
    @property
    def label(self):
        return self._prop('attribute/label')
   
    @property
    def accessible(self):
        return self._wda_prop("accessible")
```

每次获取信息的时候都需要与wda交互，调用/element或/wda/element接口

```python
class Element(object):
    def _req(self, method, url, data=None):
        return self.http.fetch(method, '/element/' + self._id + url, data)
    
    def _wda_req(self, method, url, data=None):
        return self.http.fetch(method, '/wda/element/' + self._id + url, data)
    
    def _prop(self, key):
        return self._req('get', '/' + key.lstrip('/')).value
    
    def _wda_prop(self, key):
        ret = self.http.get('/wda/element/%s/%s' % (self._id, key)).value
        return ret
```

wda支持如下操作接口：

![image-20210708182958362](/assets/img/image-20210708182958362.png)

而如果对Element元素进行点击，会有两种方式：一种是直接调用wda的click接口，另一种是先获取元素的中心点坐标，然后点击坐标。理论上前一种速度更快。

```python
class Element(object):
    def tap(self):
        return self._req('post', '/click')
        
    def click(self):
        """
        Get element center position and do click, a little slower
        """
        # Some one reported, invisible element can not click
        # So here, git position and then do tap
        x, y = self.bounds.center
        self._session.click(x, y)
```

### 二、层级设置

wda支持一个设置：*snapshotMaxDepth*，用于指定查找元素的层级。

对于页面上元素过多，导致查找超时的情况，可以通过修改snapshotMaxDepth来加快查询速度。

在wda中通过*/session/$sessionId/appium/settings* 接口可以设置snapshotMaxDepth：

![image-20210708183553430](/assets/img/image-20210708183553430.png)

![image-20210708183619848](/assets/img/image-20210708183619848.png)

python调用appium_settings来修改snapshotMaxDepth

```python
wda_client.appium_settings({"snapshotMaxDepth": 30})

class BaseClient(object):
     def appium_settings(self, value: Optional[dict] = None) -> dict:
        """
        Get and set /session/$sessionId/appium/settings
        """
        if value is None:
            return self._session_http.get("/appium/settings").value
        return self._session_http.post("/appium/settings",
                                       data={
                                           "settings": value
                                       }).value
```

一个简单的脚本，逐级获取当前页面下所有元素，写入一个csv文件

```python
""" 获取当前页的元素，写入文件 """
import wda

wda_client = wda.Client('http://localhost:%s' % 20002)
s = wda_client.session()
result = {}

def parse(root, result, depth):
    if root.get('label'):
        alias = root.get('label')
        if alias in result.keys():
            if not result[alias]['type'] == root.get('type'):
                result[alias + '_' + root.get('type')] = {
                    'label': root.get('label'),
                    'name': root.get('name'),
                    'value': root.get('value'),
                    'type': root.get('type'),
                    'depth': depth
                }
        else:
            result[alias] = {
                'label': alias,
                'name': root.get('name'),
                'value': root.get('value'),
                'type': root.get('type'),
                'depth': depth,
            }

def get_source(depth):
    s.appium_settings({"snapshotMaxDepth": depth})
    root = s.source(format='json')
    queue = [root]
    while queue:
        item = queue.pop(0)
        parse(item, result, depth)
        if item.get('children'):
            queue.extend(item.get('children'))

def get_all_source(max_depth):
    for i in range(10, max_depth, 10):
        get_source(i)
    get_source(max_depth)

def write_csv(page):
    with open(page + '.csv', 'w', encoding='gbk') as f:
        f.write('alias,label,name,value,type,max_depth\n')
        for key in result.keys():
            i = result[key]
            f.write('{},{},{},{},{},{}\n'.format(key, i['label'], i['name'], i['value'], i['type'], i['depth']))

if __name__ == '__main__':
    page_name = input('Please input a page:')
    while page_name:
        d = input('Please input max_depth:')
        if d:
            max_depth = int(d)
        else:
            max_depth = 50
        get_all_source(max_depth)
        write_csv(page_name)
        page_name = input('Please input a page:')
```

### 三、平衡速度与容错

自动化测试中，需要平衡查找速度与失败重试。

（1）压缩无用操作,直接调用Selector的find_element_ids()方法

```python
# 调用查找元素
s = Selector(label='登录')
elems = s.find_element_ids()

# 根据出现顺序获取Element对象。 order=1,2,3……
elem = elems[order-1]

# click操作
elem.tap()
```

(2) 指定查找元素的超时时间和重试次数

```python
# 弹窗检测：只查一次  internal=0.5,retry=1

# 元素assert 检测： 
    # 刚操作完，页面有刷新，直到检测到： internal=0.5, retry=5
    # 静止页面： internal=0.5,retry=1
# 操作调用检测： 
    # 静止页面： internal=0.3,retry=5
    # 刚操作完:  internal=1,retry=5

def find_element_new(self, element=None, **kwargs):
    """
    优化后的元素查找。
    """
    timeout = kwargs.pop('timeout') if 'timeout' in kwargs else 1.0
    order = kwargs.pop('order') if 'order' in kwargs else 1
    retry = kwargs.pop('retry') if 'retry' in kwargs else 1
    if element:
        s = self.wda_client(element.find)
    else:
        s = self.wda_client(**kwargs)
    return s.get(timeout=timeout, retry=retry, raise_error=False, order=order)
```

（3）其他操作复用

```python
def click_new(self,  element: Element = None, **kwargs):
    tap = kwargs.pop('tap') if 'tap' in kwargs else True
    e = self.find_element_new(element, **kwargs)
    if e:
        logger.debug('find element result: [%s]', e.label)
        e.tap() if tap else e.click()
    else:
        # 用于错误处理的时候
        raise FindElementError('点击失败')

def input_new(self, element: Element = None, context='', **kwargs):
    e = self.find_element_new(element, **kwargs)
    if e:
        logger.debug('find element result: [%s]', e.label)
        e.set_text(context)
    else:
        # 用于错误处理的时候
        raise FindElementError('输入内容失败')

def find_matches_new(self, elements: List[Element], **kwargs):
    """
    find_matches_new([xxx页.x按钮,xxx页.y按钮],'A标签'={'label':'A','type:'Button'}}
    """
    result = {}
    for e in elements:
        s = self.wda_client(e.find)
        find_e = s.find_element_ids()  # 只查一次
        result[e.find] = find_e
    for name in kwargs:
        s = self.wda_client(**kwargs[name])
        find_e = s.find_element_ids()  # 只查一次
        result[name] = find_e
    return result
```