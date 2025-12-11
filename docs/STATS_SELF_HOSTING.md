# 自托管 GitHub Stats 指南

为确保 README 中的统计图表长期稳定，可按以下步骤搭建自托管的 `github-readme-stats` 服务并结合 Actions 定时刷新。

## 1. Fork 并部署
1. Fork [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats)。
2. 在 Vercel（推荐）/Render/Cloudflare Pages 创建新项目，来源选择刚才的 fork。
3. 在部署平台配置环境变量：
   - `PAT_1`：GitHub Fine-grained PAT（至少勾选 `read:user`、`repo:status`）。
   - `CACHE_SECONDS`：可选，默认 1800 秒。
4. 部署完成后记录生产域名，例如 `https://stats.jdwa.dev`。

## 2. 更新 README / Workflow
- 将 README 中 `STATS_BASE_URL` 设置为自定义域名（例如 `https://stats.jdwa.dev`）。
- 更新 `.github/workflows/update-readme.yml` 中的 `STATS_BASE_URL`，确保 Actions 使用自托管实例。

## 3. 定时刷新缓存
- 当前仓库的 `Update Profile README` workflow 默认每 6 小时运行一次，会调用 `scripts/update_readme.py` 自动生成统计区块。
- 也可在自托管平台（如 Vercel Cron Jobs）中添加定时请求，保持缓存常新。

## 4. 可选：多实例容灾
- 为防止单一实例宕机，可再部署一个备份域名，并在 README 中提供回退链接。
- `scripts/update_readme.py` 支持通过环境变量覆盖 `STATS_BASE_URL`，方便在不同环境下切换。

完成以上步骤后，Profile README 内的所有统计组件将由自有实例提供，避免公共服务限流导致的加载失败。EOF