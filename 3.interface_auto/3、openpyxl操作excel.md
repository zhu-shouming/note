- 安装openpyxl

  > pip install openpyxl

##### 1、Excel中的三大对象

- WorkBook：工作薄对象
- Sheet：表单对象
- Cell：表格对象

##### 2、openpyxl对Excel的操作

- 创建工作薄对象

  ```python
  import openpyxl
  workbook = openpyxl.load_workbook(r'cases.xlsx')	# 读取已有表格
  ```

- 获取表单对象

  ```python
  sh = workbook['表单名']	# 选择已有的表单获取表单对象
  ```

- 表格数据读取或写入

  ```python
  cell = sh.cell(row=1, column=1).value	# 获取一行一列表格里的值
  sh.cell(row=1, column=2).value = 'xx'	# 给一行二列表格里赋值
  workbook.save(r'cases.xlsx')	# 写完数据保存才能生效，需要用工作薄对象保存
  sh.max_row	# 获取表单最大行数
  sh.max_column	# 获取表单最大列数
  sh.rows	# 获取表单所有内容，每一行存放在一个元组中
  ```

##### 3、封装操作excel

```python
class CaseData:
    def __init__(self, *args):
        for i in list(*args):
            setattr(self, i[0], i[1])   # 通过反射机制为对象设值


class ReadExcel:
    def __init__(self, file_name, sheet_name):
        """
        :param file_name: excel文件名
        :param sheet_name: sheet表单名
        """
        self.file_name = file_name
        self.sheet_name = sheet_name

    def open(self):
        """打开工作薄和表单"""
        self.wb = openpyxl.load_workbook(self.file_name)
        self.sh = self.wb[self.sheet_name]

    def read_data(self):
        """
        读取表单数据
        :return: [dict1,dict2...]
        """
        self.open()
        rows = list(self.sh.rows)
        titles = [i.value for i in rows[0]]
        cases = []
        for i in rows[1:]:
            datas = [j.value for j in i]
            cases.append(dict(zip(titles, datas)))
        return cases

    def read_data_obj(self):
        """
        读取变淡数据，每一条数据存储到一个对象上
        :return:[obj1, obj2...]
        """
        self.open()
        rows = list(self.sh.rows)
        titles = [i.value for i in rows[0]]
        cases = []
        for i in rows[1:]:
            datas = [j.value for j in i]
            cases.append(CaseData(zip(titles, datas)))
        return cases
    
        def write_data(self, row, column, value):
        """
        写入数据到excel
        :param row: 写入的行
        :param column: 写入的列
        :param value: 写入的值
        """
        self.open()
        cell = self.sh.cell(row=row, column=column)
        cell.value = value
        self.wb.save(self.file_name)
```



