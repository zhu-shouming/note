####  	 	1、HTML页面结构

> 超文本标记语言的结构包括"头"部分(**Head**)和“主体”部分(**Body**)，其中“头”部提供关于网页标题等信息，“主体”部分提供网页的具体内容

##### 1、文档声明

> DOCTYPE声明该html文件使用的HTML版本

##### 2、页面头部

> <head>标签负责对网页进行一些设置以及定义标题，设置包括定义网页的编码方式、外链css样式及javascript文件等

##### 3、页面内容

> <body>元素定义文档的主体，也就是页面显示的内容

#### 2、常见的HTML标签

##### 1、注释:<!-- -->

##### 2、标题标签

- h1~h6定义标题

##### 3、段落和换行标签

- p：标签定义段落，元素会自动在其前后创建一些空白
- br：插入一个简单的换行符。标签是空标签，它没有结束标签。
- hr；标签在HTML页面中创建一条水平线。在HTML中没有结束标签。

##### 4、块标签

- div标签：标签块元素，表示一块内容，没有具体的含义。

  div标签可以把文档分割成独立的、不同的部分。

- span标签：行内元素，表示一行中的一小段内容，没有具体的含义。

  span没有固定的格式表现，当对其应用样式时，会产生视觉上的效果。

##### 5、含样式和语义的行内标签

| **标签** | **含义**                                     |
| -------- | -------------------------------------------- |
| <i>      | 行内元素，字体斜体                           |
| <em>     | 行内元素，语义为强调内容，表示重要(倾斜效果) |
| <b>      | 行内元素，字体加粗                           |
| <strong> | 行内元素，语义为强调内容，表示重要(加粗效果) |

##### 6、图像标签&链接标签

- img标签：向网页中嵌入一幅图像

  <img>标签有两个必须的属性：src属性和alt属性

  ```html
  <img src="http://www.baidu.com" alt="baidu"/>
  ```

  | **属性** | **描述**           |
  | -------- | ------------------ |
  | `src`    | 规定显示图像的url  |
  | `alt`    | 规定图像的替代文本 |
  | height   | 定义图像的高度     |
  | width    | 设置图像的宽度     |

- a标签：定义超链接，用于从一个链接跳转到另一个页面

  <a>标签最重要的属性是href属性，表示链接的目标

  ```html
  <a src="http://www,baidu.com">点击链接跳转到百度</a>
  ```

- link标签(放在头部)

  链接到一个外部样式

##### 7、音频标签&视频标签

- audio
- video

##### 8、列表

- 有序列表

  在网页上定义一个有编号的内容列表可以用<ol>、<li>来实现

  ```html
  <ol>
      <li>列表文字一</li>
      <li>列表文字二</li>
  </ol>
  ```

- 无序列表

  在网页上定义一个无编号的内容列表可以用<ul>、<li>来实现

  ```html
  <ul>
      <li><a href="#">标题1</a></li>
      <li><a href="#">标题2</a></li>
  </ul>>
  ```

##### 9、表格

- table：定义HTML表格

  简单的HTML表格由table元素以及一个或多个tr、th或td元素组成

  tr元素定义表格行，th元素定义表头，td定义单元格

  ```html
  <table border="1">
      <tr>
      	<th>name</th>
          <th>age</th>
      </tr>
      <tr>
      	<td>xiaoming</td>
          <td>18</td>
      </tr>
  </table>
  ```

#### 3、HTML表单

##### 1、form标签

- form：标签用于为用户输入创建HTML表单，表单能够包含input元素，比如文本字段、复选框、单选框、提交按钮等。

  form标签的属性：

  | 属性   | 描述               |
  | ------ | ------------------ |
  | action | 定义表单提交的地址 |
  | method | 定义表单提交的方式 |

- form表单中包含的元素

  | 元素标签   | 作用                                         |
  | ---------- | -------------------------------------------- |
  | <label>    | 为表单元素定义文本标注                       |
  | <input>    | 定义通用的表单元素                           |
  | <textarea> | 定义多行文本输入框                           |
  | <select>   | 定义下拉表单元素                             |
  | <option>   | 与<select>标签配合，定义下拉表单元素中的选项 |

##### 2、input标签

- value属性：定义表单元素的值

- name属性：定义表单元素的名称，此名称是提交数据时的键名

  ```html
  <form>
      <p>
          <lable>账号</lable>
          <input type="text" name="username" id="user" />
      </p>
      <p>
          <lable>密码</lable>
          <input type="text" name="password" id="password" />
      </p>
  </form>
  ```

- type属性

  | 值       | 作用                                        |
  | -------- | ------------------------------------------- |
  | text     | 定义单行文本输入框                          |
  | password | 定义密码输入框                              |
  | radio    | 定义单选框                                  |
  | checkbox | 定义复选框                                  |
  | file     | 定义上传文件                                |
  | submit   | 定义提交按钮                                |
  | button   | 定义一个普通按钮                            |
  | reset    | 定义重置按钮                                |
  | image    | 定义图片作为提交按钮，用src属性定义图片地址 |
  | hidden   | 定义一个隐藏的表单域，从来存储值            |

##### 3、label标签

<label>标签为input元素定义标注

label元素不会向用户呈现任何特殊的效果，不过它为鼠标用户改进了可用性。如果在label元素内点击文本，就会触发控件，浏览器会自动把焦点转到和标签相关的表单控件上。

<label>标签的for属性应当与相关元素的id属性相同

```html
<form>
    <label for="user">账号</label>
    <input type="text" name="username" id="user" />
</form>
```

##### 4、textarea标签

<textatea>标签哦按定义多行的文本输入控件

textarea属性

| 属性        | 值               | 描述                             |
| ----------- | ---------------- | -------------------------------- |
| autofocus   | autofocus        | 规定页面加载文本区域自动获得焦点 |
| cols        | number           | 规定文本区内的可见宽度           |
| disabled    | disabled         | 规定禁用该文本                   |
| maxlength   | number           | 规定文本区域的最大字符数         |
| form        | form_id          | 规定文本区域所属的一个或多个表单 |
| name        | name of textarea | 规定文本区的名称                 |
| placeholder | text             | 规定描述文本区域预期值的简短提示 |
| readonly    | readonly         | 规定文本区为只读                 |
| required    | required         | 规定文本区域是必填的             |
| rows        | number           | 规定文本区域内的可见行数         |

##### 5、select标签

select元素可创建单选或多选菜单，也可以用于选择数据提交表单

`<select>`元素中的<option></option>标签用于定义列表中的可用选项

```html
<form>
    <select name='skill'>
       <option value='py'>python</option> 
        <option value='ht'>html</option> 
        <option value='css'>css</option> 
    </select>
</form>
```

##### 6、option标签

option元素定义下拉列表中的一个选项，option位于select元素内部

#### 4、内联框架

##### 1、iframe

iframe元素会创建包含另一个文档的内联框架

