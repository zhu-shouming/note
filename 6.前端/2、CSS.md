#### 一、html引入css的方式

1. 标签内引入（内联样式），优先级最高

```html
<h2 style="color: #FF0000;">大家好</h2>
```

2. html头部标签内引入（内部样式表），优先级其次

```html
<head>
		<meta charset="utf-8">
		<style type="text/css">
			:root{
				background: #ffff7f;
			}
		</style>
</head>
```

3. 外部css文件引入，优先级最低

```html
<head>
		<meta charset="utf-8">
		<link rel="stylesheet" type="text/css" href="css_style/index.css"/>
</head>
```

#### 二、css语法

##### 1.css由选择器和声明块组成

```css
/*选择器{属性1:值1;属性2:值2；}*/
h1{color: red;text-align: center;}
```

##### 2.css选择器

- 简单选择器：根据名称、id、类来选取元素
- 组合器选择器：根据他们之间的特定的关系来选取元素
- 伪类选择器：根据特定状态选取元素
- 伪元素选择器：选取元素的一部分并设置其样式 
- 属性选择器： 根据属性或属性值来选取元素 

##### 3.简单选择器

- 元素选择器：设置h1、h2、p元素的样式，具有相同样式的元素可进行分组

  ```css
  h1, h2, p{
    text-align: center;
    color: red;
  }
  ```

- id选择器：设置id=para1元素的样式

  ```css
  #para1 {
    text-align: center;
    color: red;
  }
  ```

- 类选择器：设置具有class=center属性的P标签样式

  ```css
  p.center {
    text-align: center;
    color: red;
  }
  ```

- 通过选择器：css规则会影响页面上的每个html元素

  ```css
  * {
    text-align: center;
    color: blue;
  }
  ```

#### 三、设置颜色

##### 1.背景颜色

```css
<h1 style="background-color:DodgerBlue;">China</h1>
```

##### 2.字体颜色

```css
<h1 style="color:Tomato;">China</h1>
```

##### 3.边框颜色

```css
<h1 style="border:2px solid Tomato;">Hello World</h1>
```

##### 4.设置颜色的方式

- 十六进制表示：#ff5500
- 英文表示：red
- rgb()表示：rgb(255,255,255)

#### 四、背景

- background-color
- background-image
- background-repeat
- background-attachment
- background-position

```css
body {
  	background-color: lightblue;	/* 设置背景颜色 */ 
    opacity:0.3;	/* 设置指定元素透明度，取值范围0.0-1.0，值越低越透明 */
    background-image: url("...");	/* 设置元素背景的图片，图片会重复 */
    background-repeat: repeat-x;	/* repeat-x:横轴重复，repeat-y：垂直重复，no-repeat：只显示一次背景图像 */
    background-position: right top;	/* 指定图像的位置 */
    background-attachment: fixed; /* fixed:固定图像，scroll：随页面滚动 */
}
```

**background-简写属性**

```css
body{
    background: lightblue url("...") no-repeat right top;	/* 按照color、image、repeat、attachment、position排序即可 */
}
```

#### 五、字体

##### 1.文本颜色和背景色

```css
h1 {
  background-color: black;
  color: white;
}
```

##### 2.文本对齐

```css
h1 {
  text-align: center;	/* center:居中对齐,left:左对齐。right：右对齐 */
}
```

##### 3.字体大小

em：相对长度单位，参照**父类容器字号大小**或浏览器默认字号大小。

rem：CSS3新标准相对长度单位，参照**HTML根标签**的字号大小。

设备像素：又称物理像素，物理像素是固定不变的。

css像素：又称逻辑像素，是一个抽象个概念，单位是px。

DPR=设备像素/css像素，DPR越高，显示越清晰

```css
h1 {
  font-size: 40px;
}
```