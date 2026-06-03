# Acroform PDF 提取指南（政务服务类）

> 适用场景：工信部政务服务平台、各省政务网站的 PDF 表单文档

## 问题

政务平台 PDF 表单（acroform）内容被 FlateDecode 压缩，导致：
- `strings` 只能看到乱码（中文字符被压缩编码）
- `pymupdf.get_text('text')` 超时或返回空（27页 PDF 直接卡死）
- `web_extract` 不支持本地文件
- `marker-pdf` 需要 5GB 模型，不划算

## 解法

**PaddleOCR-VL** 能直接识别表单中的文字，输出 Markdown。

```bash
# 使用 PaddleOCR-VL 提取 PDF 文字
# 输出示例：./output/文件名_by_PaddleOCR-VL-1.6.md
```

## 产出格式

OCR 结果按页输出 HTML 表格，每页一个 `<table>`，结构清晰，可直接 grep/解析。

## 适用判断

| PDF 类型 | 推荐工具 | 原因 |
|---------|---------|------|
| 文字型 PDF（可选中） | pymupdf | 快，无依赖 |
| 扫描件/图片型 | marker-pdf | 准确，但重 |
| 政务 acroform 表单 | PaddleOCR-VL | FlateDecode 压缩内容无法用 pymupdf 读取 |
