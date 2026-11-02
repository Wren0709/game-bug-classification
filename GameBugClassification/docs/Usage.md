# 使用说明

这是一个可以独立运行的 Python 分类练习项目，输出 CSV 复核表，不包含团队网页。

## 安装

解压后进入 `game_bug_classification` 文件夹，使用 Python 3.11 或更新版本：

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python validate_data.py
python -m unittest discover -s tests -v
```

上面的激活命令用于 Windows。macOS 和 Linux 使用 `source .venv/bin/activate`。

## 运行模拟反馈

```text
python workbench.py --input examples/sample_feedback.csv --id-col report_id --log-col log_excerpt --logs-dir examples
```

结果在 `private/workbench_results.csv`。打开后填写 `reviewed_category`，可选 Audio、Gameplay、Network、Performance、UI。保存为 UTF-8 CSV 后运行：

```text
python review_results.py
```

最终结果在 `private/reviewed_results.csv`。清空人工分类后，条目会重新变成待复核；没有描述的条目显示 unresolved。预测结果不会自动变成最终分类。

再次运行时，已有结果不会被覆盖。可以用 `--output private/另一个文件名.csv` 输出新文件，或明确使用 `--overwrite` 覆盖。

## 导入自己的表格

把文件放在 `incoming` 文件夹，指定描述列：

```text
python workbench.py --input incoming/feedback.xlsx --text-col "玩家描述" --output private/my_review.csv
```

需要保留编号或来源链接时，再添加 `--id-col "编号"`、`--url-col "反馈链接"`。未选择的邮箱、玩家账号等列不会跟随导出。原始描述仍可能包含个人信息，分享前需要人工检查，不能把这个功能当作自动脱敏。

日志只提取关键词，不确认根因。日志文件填写在 `log_file` 列，通过 `--logs-dir incoming/logs` 指定目录。只读取目录内的 txt 或 log 文件，读取长度最多 100,000 个字符；缺失和截断会注明。

## 查看评估

`output` 保存随包模拟数据的评估结果。运行 `python main.py` 可以重新评估，新结果保存在 `private/evaluation`。本次复核的测试集准确率为 60.0%，五折平均准确率为 68.6%，只适用于这组模拟数据，不代表真实反馈的分类正确率。

## 上传 GitHub

上传压缩包内 `game_bug_classification` 文件夹的内容。不要把真实数据、`private`、`incoming` 或 `.venv` 上传。README 和 `docs/UploadInstructions.md` 有具体步骤。
