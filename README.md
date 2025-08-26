# ButterKnife迁移工具

一个用于将Android项目中的ButterKnife框架迁移到findViewById或ViewBinding的Python工具。

## 功能特性

- 🔍 **智能扫描**: 自动扫描项目中的Java文件，识别包含ButterKnife注解的文件
- 📝 **注解解析**: 使用正则表达式解析@BindView和@OnClick注解
- 🔄 **代码转换**: 将ButterKnife注解转换为标准的Android代码
- 💉 **代码注入**: 自动在合适的方法中注入初始化代码
- 💾 **备份支持**: 自动备份原始文件，支持回滚操作
- 📊 **详细报告**: 生成完整的迁移报告和统计信息

## 支持的转换

### @BindView注解
```java
// 转换前
@BindView(R.id.submit)
Button submitButton;

// 转换后
Button submitButton;

// 在onCreate方法中自动添加
submitButton = (Button) findViewById(R.id.submit);
```

### @OnClick注解
```java
// 转换前
@OnClick({R.id.submit, R.id.cancel})
public void onButtonClick(View view) {
    // 处理逻辑
}

// 转换后
public void onButtonClick(View view) {
    // 处理逻辑
}

// 在onCreate方法中自动添加
submitButton.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        onButtonClick(v);
    }
});
```

## 安装和使用

### 1. 克隆项目
```bash
git clone <repository-url>
cd butterknife_migrator
```

### 2. 运行迁移工具
```bash
# 使用默认配置
python main.py

# 指定项目路径
python main.py --project-path /path/to/android/project

# 指定绑定模式
python main.py --binding-mode findViewById

# 启用备份
python main.py --backup

# 详细输出
python main.py --verbose
```

### 3. 命令行参数
- `--config, -c`: 配置文件路径
- `--project-path, -p`: Android项目路径
- `--binding-mode, -b`: 绑定模式 (findViewById 或 viewBinding)
- `--backup`: 启用备份功能
- `--verbose, -v`: 详细输出

## 配置文件

创建配置文件 `butterknife_migrator_config.json`:

```json
{
  "PROJECT_PATH": "/path/to/android/project",
  "BINDING_MODE": "findViewById",
  "BACKUP_ENABLED": true,
  "LOG_LEVEL": "INFO",
  "SCAN_DIRECTORIES": [
    "app/src/main/java",
    "src/main/java"
  ],
  "EXCLUDE_DIRECTORIES": [
    "build",
    ".gradle",
    ".idea"
  ]
}
```

## 项目结构

```
butterknife_migrator/
├── main.py                 # 主控制文件
├── config.py              # 配置管理
├── scanner/               # 文件扫描模块
│   ├── __init__.py
│   └── file_scanner.py
├── parser/                # 注解解析模块
│   ├── __init__.py
│   └── butterknife_parser.py
├── transformer/           # 代码转换模块
│   ├── __init__.py
│   ├── base_transformer.py
│   ├── findview_transformer.py
│   ├── onclick_transformer.py
│   └── bindcall_remover.py
├── injector/              # 代码注入模块
│   ├── __init__.py
│   └── code_injector.py
├── writer/                # 文件写入模块
│   ├── __init__.py
│   └── file_writer.py
├── utils/                 # 工具模块
│   ├── __init__.py
│   └── logger.py
└── tests/                 # 测试文件
```

## 工作流程

1. **扫描阶段**: 遍历项目目录，找到所有Java文件
2. **解析阶段**: 分析文件内容，提取ButterKnife注解信息
3. **转换阶段**: 应用各种转换器，将注解转换为标准代码
4. **注入阶段**: 在合适的方法中注入初始化代码
5. **写入阶段**: 将转换后的代码写回文件，生成备份

## 转换器说明

### FindViewTransformer
- 将@BindView注解转换为字段声明
- 生成findViewById初始化代码
- 支持在onCreate、onViewCreated等方法中注入

### OnClickTransformer
- 将@OnClick注解转换为setOnClickListener调用
- 生成匿名内部类实现点击事件
- 保持原有的事件处理逻辑

### BindCallRemover
- 删除ButterKnife.bind()调用
- 清理ButterKnife相关的import语句
- 优化代码结构

## 日志和报告

工具会生成详细的迁移日志和报告：

- 控制台实时输出迁移进度
- 文件日志记录所有操作
- JSON格式的迁移报告
- 备份文件管理

## 注意事项

1. **备份重要**: 迁移前请确保项目已备份
2. **测试验证**: 迁移完成后请测试应用功能
3. **代码审查**: 建议人工检查转换后的代码
4. **依赖清理**: 记得从build.gradle中移除ButterKnife依赖

## 故障排除

### 常见问题

1. **文件编码问题**: 确保Java文件使用UTF-8编码
2. **权限问题**: 确保有读写项目文件的权限
3. **路径问题**: 检查项目路径配置是否正确

### 调试模式

使用 `--verbose` 参数启用详细输出：

```bash
python main.py --verbose --project-path /path/to/project
```

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 许可证

本项目采用MIT许可证。
