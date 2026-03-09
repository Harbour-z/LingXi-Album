# 第三方库 CVE 漏洞扫描报告（模板）

状态：模板（需在发布前实际执行并粘贴原始结果）  
生成时间：TBD  
执行人：TBD  
环境：TBD（OS/CPU/网络）  

## 1. 扫描范围

- 后端 Python 依赖：`requirements.txt`
- 前端 Node 依赖：`frontend/package.json` + `package-lock.json`
- Docker 镜像（如发布）：`backend`、`frontend`、`qdrant`（如自建镜像）

## 2. 工具与命令（示例）

### 2.1 Python

- pip-audit（建议）
  - 输入：requirements.txt
  - 输出：JSON + 人工摘要

### 2.2 Node

- npm audit（建议）
  - 输入：package-lock.json
  - 输出：JSON + 人工摘要

### 2.3 镜像扫描

- Trivy 或 Grype（建议）
  - 输入：镜像 tag 或 tar
  - 输出：SARIF/JSON + 人工摘要

## 3. 扫描结果摘要（需填写）

| 范畴 | Critical | High | Medium | Low | 处理结论 |
|---|---:|---:|---:|---:|---|
| Python 依赖 | TBD | TBD | TBD | TBD | TBD |
| Node 依赖 | TBD | TBD | TBD | TBD | TBD |
| Docker 镜像 | TBD | TBD | TBD | TBD | TBD |

## 4. 关键漏洞清单（需填写）

| CVE | 组件 | 受影响版本 | 修复版本 | 风险描述 | 处置（升级/替换/豁免） | 证据 |
|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | 原始扫描输出截图/JSON |

## 5. 原始输出存档（路径约定）

- `appendix/security/cve_raw/python_pip_audit.json`
- `appendix/security/cve_raw/node_npm_audit.json`
- `appendix/security/cve_raw/image_trivy.json`

