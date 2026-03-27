# 数据映射规则

在把提取出来的 Markdown 转换为 `template/data.json` 时，请参考本文件。

## 源文件

- 字段结构（Schema）：`../../template/data_template.json`
- 输出风格示例：`../../template/data_demo.json`

## 规则

1. 仅使用「提取的 Markdown」或「导出的页面图片人工目检」能够支持的事实信息。
2. 不要臆造：雇主/公司、学校、日期、职位、联系方式、成果、技能要点等。
3. 缺失或不确定的标量字段请保持为 `""`。
4. 缺失的列表段落请保持为 `[]`。
5. 尽量保留源语言：如果 PDF 是中文，则 `description`、`company`、`project_name` 等字段保持中文表达。
6. `name_py` 可以来自 PDF 中明确写出的英文名；如果只有中文姓名，允许将其转写为不带声调、首字母大写的拼音（title case）。
7. 不要推导带时效性的字段，除非源文件明确写出。特别是：与其从日期计算，不如优先把 `age`、`work_year` 留空。
8. 经验条目的顺序尽量与源文件一致；除非 PDF 明确按时间分区且已按“最新在前”排序。
9. 对 `skills`、`content`、`achievement`：每个 bullet 独立成一条记录，`index` 由规范化脚本统一顺序重写。
10. 当某条 bullet 同时混合了“职责”和“结果/产出”时，建议按如下方式拆分：
   - `content`：职责、任务、范围、过程性工作
   - `achievement`：结果、影响、指标、奖项、成功交付
11. 如果一个段落只有职责类 bullet，缺少明确产出/成果，则将 bullet 放在 `content` 下，`achievement` 留空。
12. 仅在上下文明显且含义明确时，才修正明显的 OCR 错误。

## 建议操作顺序

1. 阅读提取的 Markdown。
2. 打开 `../../template/data_template.json`。
3. 打开 `../../template/data_demo.json`。
4. 起草候选 JSON。
5. 在渲染前，对候选文件运行 `../scripts/normalize_resume_data.py`。
