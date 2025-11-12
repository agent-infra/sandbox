  Dataset 评测用例总览

  1. evaluation_ping.xml - 基础连通性测试

  - 测试 aio 系统版本获取:回答 aio 系统的版本号

  2. evaluation_basic.xml - 单工具基础能力测试

  A. 环境探测类

  - 检查 Python 包 'fastapi' 是否已安装
  - 统计已安装的 Python 包数量

  B. 文件操作类

  - 创建文件并写入内容 "Hello MCP",然后读取
  - 列出 /tmp 目录中以 'test_eval' 开头的文件数量
  - 搜索文件中 'Hello MCP' 模式的匹配次数

  C. 代码执行类

  - 执行 Python 代码计算 2^10
  - 计算 1-100 内所有偶数的和
  - 统计字符串 "Model Context Protocol" 中的元音字母数量

  D. Shell 操作类

  - 执行 bash echo 命令输出 "MCP_TEST"
  - 使用 bash 统计 /tmp 目录中的文件夹数量

  3. evaluation_browser.xml - 浏览器基础测试

  - 导航到 bytedance.com,检查是否包含 'ByteDance' 或 '字节跳动'
  - 导航到 bytedance.com,统计页面链接数量
  - 导航到 baidu.com,用 JavaScript 获取链接数量
  - 导航到 baidu.com,用 JavaScript 获取页面标题
  - 导航到 baidu.com,统计 DOM 中的 anchor 元素数量
  - 测试表单填充:在 baidu.com 搜索框填入 'test_search'
  - 测试表单填充工作流:填入 'MCP test' 并验证
  - 测试完整浏览器工作流:导航、读取链接、获取 markdown、执行 JS
  - 测试标签页管理:创建新标签页并统计数量
  - 测试标签页切换:切换标签页并获取标题
  - 搜索 "aio sandbox",导航到 GitHub 页面,输出主要贡献者
  - 获取浏览器下载列表并统计数量
  - 触发下载并检查下载列表是否包含文件
  - 检查下载项是否包含 'filename' 字段

  4. evaluation_browser_advanced.xml - 浏览器高级交互测试

  A. 元素点击操作

  - 点击按钮并验证文本变化
  - 点击多个按钮中的特定按钮(使用索引)

  B. 表单填充与提交

  - 填充文本输入框和邮箱输入框

  C. 键盘操作

  - 测试按键事件(Enter 键)
  - 测试特殊按键(Tab 键)
  - 测试组合键(Delete 键)

  D. 鼠标移动与悬停

  - 测试鼠标悬停事件
  - 测试悬停菜单显示
  - 测试悬停 tooltip 显示

  E. 滚动操作

  - 测试页面滚动
  - 测试负向滚动(向上滚动)
  - 测试滚动到底部

  F. 导航历史

  - 测试后退功能
  - 测试前进功能

  G. 标签页管理

  - 关闭标签页并统计剩余数量
  - 切换标签页后关闭
  - 测试关闭最后一个标签页的行为

  H. 下拉选择

  - 测试下拉菜单选择
  - 测试通过索引选择下拉选项

  I. 复杂交互场景

  - 测试计算器交互:填充数字并执行加法运算

  J. 可点击元素获取

  - 过滤特定类型的可点击元素
  - 获取复杂页面中的所有可交互元素

  K. 浏览器信息获取

  - 获取浏览器视口信息
  - 获取 CDP URL
  - 计算视口面积

  5. evaluation_code_advanced.xml - 代码执行高级测试

  A. JavaScript 基础执行

  - 基础算术运算
  - 字符串反转操作

  B. JavaScript 对象和数组

  - 数组求和操作
  - JSON 解析

  C. Python 高级特性

  - 列表推导式计算平方和
  - 字典值求和
  - lambda 和 map 函数使用

  D. 文件操作 + 代码执行

  - Python 文件 I/O 操作

  E. JavaScript 异步代码

  - 同步循环求和

  F. 错误处理

  - Python 异常捕获(ZeroDivisionError)
  - JavaScript 错误处理(JSON 解析错误)

  G. 数学运算

  - Python math 库使用
  - JavaScript Math 操作

  H. 字符串处理

  - Python 正则表达式匹配邮箱
  - JavaScript 正则表达式匹配数字

  I. 数据结构

  - Python 集合交集操作

  J. 综合场景

  - Python 数据处理管道
  - JavaScript 函数式编程

  6. evaluation_collaboration.xml - 多工具协作测试

  E. 文件+代码执行

  - 读取文件并统计 'async' 出现次数
  - 创建并执行斐波那契数列脚本

  F. Shell+文件操作

  - 创建目录和文件,然后读取
  - 获取当前工作目录并写入文件

  G. 环境探测+代码分析

  - 获取包列表并统计包含 'fast' 的包数量

  H. Browser + 文件操作

  - 创建 HTML 文件并用浏览器导航验证

  I. 编辑器 + 代码执行

  - 使用编辑器创建 Python 文件并执行
  - 修改文件后重新执行

  J. 复杂多步协作

  - bash + 文件 + 代码执行管道
  - 获取上下文并写入文件验证版本号

  K. 浏览器 + 代码分析

  - 浏览器 evaluate + Python 处理 DOM 数据

  L. 文件查找 + 处理

  - 批量处理文件
  - 文件搜索和聚合统计

  7. evaluation_editor.xml - str_replace_editor 工具测试

  A. 文件查看 (view)

  - 查看完整文件内容
  - 查看指定行范围

  B. 文件创建 (create)

  - 创建新的 Python 文件

  C. 字符串替换 (str_replace)

  - 单次字符串替换
  - 多行字符串替换

  D. 插入 (insert)

  - 在指定行插入内容

  E. 复杂编辑场景

  - Python 代码重构

  F. 边界情况

  - 创建空文件
  - 处理特殊字符

  G. 撤销操作 (undo_edit)

  - 基础撤销操作
  - 多次撤销操作
  - 撤销新文件创建

  8. evaluation_error.xml - 错误处理测试

  - 读取不存在的文件
  - 执行产生 ZeroDivisionError 的 Python 代码

  9. evaluation_packages.xml - 包管理工具测试

  A. Node.js 包查询

  - 检查 'express' 是否已安装
  - 统计 Node.js 包数量

  B. 混合包查询

  - 同时获取 Python 和 Node.js 包

  C. 不同语言别名

  - 使用 'node' 别名
  - 使用 'py' 别名

  D. 包搜索

  - 搜索包含特定字符串的包

  E. 版本信息

  - 提取包版本号

  F. 包统计

  - 统计所有包的总数量

  10. evaluation_util.xml - 工具测试

  - 转换网页到 markdown 格式
  - 统计 markdown 中特定词汇出现次数

  11. evaluation_workflow.xml - 真实工作场景

  H. 代码审查工作流

  - 搜索包含特定关键字的 Python 文件
  - 使用 AST 解析统计函数定义数量

  I. 数据处理管道

  - 解析 XML 并统计元素数量