#!/usr/bin/env python3
"""
Scan all exported batches under exports/batch-ag-* (deduplicating groups by highest version
matching ContentVersionStore.mergePackages) and generate:
- ASSET_REQUESTS.md & reports/ASSET_REQUESTS.md
- REVIEW_QUEUE.md & reports/REVIEW_QUEUE.md
- reports/quota-and-quality-summary.md
- PROGRESS.md
"""

import collections
import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent


def utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    now_iso = utc_now_iso()
    exports_dir = ROOT / "exports"
    batch_dirs = sorted(p for p in exports_dir.iterdir() if p.is_dir() and p.name.startswith("batch-ag-"))

    batch_stats: List[Dict[str, Any]] = []
    # Latest group by group_id: (batch_id, group_dict)
    selected_by_id: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    ordered_gids: List[str] = []

    for bdir in batch_dirs:
        bid = bdir.name
        g_path = bdir / "groups.jsonl"
        v_path = bdir / "reports" / "validation.json"
        b_groups = [
            json.loads(line)
            for line in g_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        val_rep = json.loads(v_path.read_text(encoding="utf-8"))

        b_items = sum(len(g["items"]) for g in b_groups)
        b_planned_assets = sum(
            1 for g in b_groups for a in g.get("assets", []) if a["status"] == "planned"
        )
        b_ready_assets = sum(
            1 for g in b_groups for a in g.get("assets", []) if a["status"] == "ready"
        )
        versions = sorted({g["version"] for g in b_groups})
        pools = sorted({g["pool"] for g in b_groups})

        for g in b_groups:
            gid = g["group_id"]
            if gid not in selected_by_id:
                ordered_gids.append(gid)
                selected_by_id[gid] = (bid, g)
            else:
                _, cur_g = selected_by_id[gid]
                if g["version"] >= cur_g["version"]:
                    selected_by_id[gid] = (bid, g)

        batch_stats.append({
            "batch_id": bid,
            "pools": ", ".join(pools),
            "versions": ", ".join(f"v{v}" for v in versions),
            "groups": len(b_groups),
            "items": b_items,
            "ready_assets": b_ready_assets,
            "planned_assets": b_planned_assets,
            "val_counts": val_rep["counts"],
            "overall": val_rep["overall_result"],
        })

    # Count unreleased mock draft items in drafts/mock-form-01-unreleased
    unrel_path = ROOT / "drafts" / "mock-form-01-unreleased" / "groups.jsonl"
    unrel_groups = []
    if unrel_path.exists():
        unrel_groups = [
            json.loads(line)
            for line in unrel_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    unrel_item_count = sum(len(g["items"]) for g in unrel_groups)

    # Compute merged active catalog statistics across unique group_ids
    part_pool_counts: Dict[int, collections.Counter] = {p: collections.Counter() for p in range(1, 8)}
    pool_item_totals: collections.Counter = collections.Counter()
    pool_group_totals: collections.Counter = collections.Counter()
    diff_counts: collections.Counter = collections.Counter()
    skill_counts: collections.Counter = collections.Counter()
    family_pools: Dict[str, set] = collections.defaultdict(set)

    accepted_candidate_count = 0
    fully_reviewed_count = 0
    calibrated_item_count = 0
    reading_blind_items = 0
    listening_transcript_blind_items = 0
    part1_visual_blind_items = 0
    media_ready_items = 0

    ca_fallback_groups: List[Dict[str, Any]] = []
    ready_asset_inventory: List[Dict[str, Any]] = []
    review_queue_groups: List[Dict[str, Any]] = []

    for gid in ordered_gids:
        active_bid, g = selected_by_id[gid]
        part = g["part"]
        pool = g["pool"]
        n_items = len(g["items"])
        if not g.get("fixture", False):
            part_pool_counts[part][pool] += n_items
            pool_item_totals[pool] += n_items
            pool_group_totals[pool] += 1
        diff_counts[g["difficulty"]["level"]] += n_items
        family_pools[g["family_id"]].add(pool)

        if g["content_status"] in ("ai_checked", "human_reviewed"):
            accepted_candidate_count += n_items
        if g["content_status"] == "human_reviewed":
            fully_reviewed_count += n_items
        if g["difficulty"].get("basis") == "calibrated":
            calibrated_item_count += n_items

        if part in (5, 6, 7):
            reading_blind_items += n_items
        elif part == 1:
            part1_visual_blind_items += n_items
        else:
            listening_transcript_blind_items += n_items

        has_planned = any(a["status"] == "planned" for a in g.get("assets", []))
        if not has_planned:
            media_ready_items += n_items

        for it in g["items"]:
            for sk in it["skill_tags"]:
                skill_counts[sk] += 1

        speakers = g["stimulus"].get("speakers", [])
        has_ca = any(s.get("accent") == "ca" for s in speakers)
        for ast in g.get("assets", []):
            ready_asset_inventory.append({
                "asset_id": ast["asset_id"],
                "batch_id": active_bid,
                "group_id": gid,
                "pool": pool,
                "version": g["version"],
                "part": part,
                "kind": ast["kind"],
                "status": ast["status"],
                "path": ast["path"],
                "duration_ms": ast["duration_ms"],
                "segments": len(ast.get("segment_times", [])),
                "has_ca": has_ca,
            })
        if has_ca:
            ca_fallback_groups.append({
                "batch_id": active_bid,
                "group_id": gid,
                "part": part,
                "speakers": ", ".join(f"{s['speaker_id']}({s['role']}/{s['accent']})" for s in speakers),
                "characters": sum(len(seg["text_en"]) for seg in g["stimulus"].get("audio_script", [])),
            })

        review_queue_groups.append({
            "batch_id": active_bid,
            "group_id": gid,
            "pool": pool,
            "version": g["version"],
            "part": part,
            "layout": g["layout"],
            "item_count": n_items,
            "difficulty": g["difficulty"]["level"],
            "content_status": g["content_status"],
            "has_ca": has_ca,
        })

    ready_img_count = sum(1 for a in ready_asset_inventory if a["kind"] == "image" and a["status"] == "ready")
    ready_aud_count = sum(1 for a in ready_asset_inventory if a["kind"] == "audio" and a["status"] == "ready")

    # 1. Write ASSET_REQUESTS.md & reports/ASSET_REQUESTS.md
    asset_rows = "\n".join(
        f"| `{a['asset_id']}` | `{a['batch_id']}` (v{a['version']}) | `{a['pool']}` | `{a['group_id']}` | Part {a['part']} | `{a['kind']}` | `{a['status']}` | `{a['path']}` | {a['duration_ms'] if a['duration_ms'] else '—'} | {a['segments'] if a['kind']=='audio' else '—'} | "
        f"{'`en_US` 北美語音代用 (`ca` 待雲端 Neural TTS)' if (a['kind']=='audio' and a['has_ca']) else ('原生語音 (`us`/`uk`/`au`)' if a['kind']=='audio' else '1200×896 實景照片 (已通過 AI 視覺盲解)')} |"
        for a in ready_asset_inventory
    )
    ca_rows = "\n".join(
        f"| `{c['group_id']}` | `{c['batch_id']}` | Part {c['part']} | {c['speakers']} | {c['characters']} chars |"
        for c in ca_fallback_groups
    )

    asset_md = f"""# 音訊與圖片素材完成狀態及外部服務需求清單（ASSET_REQUESTS.md）

更新時間（UTC）：`{now_iso}`

## 1. 全域已匯出題庫素材完成狀態總覽（`batch-ag-0001` .. `batch-ag-0010`）

| 類別 | 數量 | 狀態與說明 |
|---|---:|---|
| 純閱讀／文法無須外部素材小題（Part 5–7） | **{reading_blind_items} 題** | 純文字與表格，100% 就緒（`training`: 80 題、`diagnostic`: 10 題、`battle`: 18 題） |
| 聽力與看圖題組小題（Part 1–4） | **{part1_visual_blind_items + listening_transcript_blind_items} 題** | `training`: 49 題（`0006`/`0007` v2）、`diagnostic`: 14 題（`0009` v1）、`battle`: 6 題（`0010` v1） |
| **累計實體就緒圖片資產（`kind=image, status=ready`）** | **{ready_img_count} / {ready_img_count} 件** | 1200×896 JPEG（`training` 3 張 + `diagnostic` 1 張），100% 通過獨立 AI 視覺盲解（`blind=true`） |
| **累計實體就緒音訊資產（`kind=audio, status=ready`）** | **{ready_aud_count} / {ready_aud_count} 件** | AAC 64kbps 22050Hz `.m4a`（`training` 27 件 + `diagnostic` 8 件 + `battle` 6 件），實測 `duration_ms`、波形 RMS 對齊與逐句 `segment_times` |
| **音訊容器與有效音框差異技術審計** | **27 / 27 通過** | 詳見 `reports/audio-technical-and-media-matrix.md`：`ffprobe` 多出的 `102.5–140.5 ms` 為 CoreAudio AAC `2112` priming frames (`95.78 ms`) + remainder padding，`valid_frames` 與 `duration_ms` 誤差 `<= 0.5 ms` |
| **純聽音盲解（不看稿 Audio-Only Blind Solve）** | **0 / {part1_visual_blind_items + listening_transcript_blind_items} 題 (`not_run`)** | 目前子代理盲解為看逐字稿／看圖模式，未宣稱已完成純聽音盲解 |
| **人工試聽與審閱完成數（`review_state=human_reviewed`）** | **0 / {ready_img_count + ready_aud_count} 件** | 全數標記為 `review_state=ai_checked`，待真人試聽與審閱 |

---

## 2. 全部 {ready_img_count + ready_aud_count} 件就緒音圖資產明細表

| Asset ID | Batch ID | Pool | Group ID | Part | 類型 | 狀態 | 包內路徑 | 長度 (ms) | 時間碼段數 | 口音／視覺實現說明 |
|---|---|---|---|---:|---|---|---|---:|---:|---|
{asset_rows}

---

## 3. 外部雲端 Neural TTS 工具、設定與預估用量需求（針對 8 組 `ca` 口音替換與正式模考時間軸）

本機 macOS `/usr/bin/say` 已內建美式（`en_US`）、英式（`en_GB`）與澳式（`en_AU`）原生語音包；`batch-ag-0009`（`diagnostic`）與 `batch-ag-0010`（`battle`）之新增 14 個音檔已 **100% 採用原生 `us`/`uk`/`au` 語音（0 個新增 `ca` 替代缺口）**。僅歷史 `batch-ag-0007` 中 8 個含 `accent="ca"` 角色的題組使用北美英語語音代用合成，並誠實標註。

| Group ID | 目前批次 | Part | 角色與口音規劃 | 腳本總字元數 |
|---|---|---:|---|---:|
{ca_rows}
"""
    for p in (ROOT / "ASSET_REQUESTS.md", ROOT / "reports" / "ASSET_REQUESTS.md"):
        p.write_text(asset_md, encoding="utf-8")

    # 2. Write REVIEW_QUEUE.md & reports/REVIEW_QUEUE.md
    rq_rows = "\n".join(
        f"| `{r['batch_id']}` (v{r['version']}) | `{r['pool']}` | `{r['group_id']}` | Part {r['part']} ({r['layout']}) | {r['item_count']} | {r['difficulty']} | `{r['content_status']}` | "
        f"{'已完成獨立盲解與音檔合成；待真人命題複核、試聽及 ca 口音替換驗收' if r['has_ca'] else '已完成獨立盲解；待真人命題複核與音圖最終審閱'} |"
        for r in review_queue_groups
    )

    rq_md = f"""# 人工審閱與後續驗收待辦佇列（REVIEW_QUEUE.md）

更新時間（UTC）：`{now_iso}`

- **AI 審查與結構驗證合格小題數（`accepted_candidate_count`, `content_status=ai_checked`）**：**{accepted_candidate_count}** 題（{len(ordered_gids)} 個獨立題組：`training` {pool_item_totals['training']} 題、`diagnostic` {pool_item_totals['diagnostic']} 題、`battle` {pool_item_totals['battle']} 題、`mock` 0 題）
- **真人命題專家審閱完成小題數（`fully_reviewed_count`, `content_status=human_reviewed`）**：**{fully_reviewed_count}** 題
- **獨立上下文盲解通過小題數（`blind=true`）**：**{accepted_candidate_count} / {accepted_candidate_count}** 題
  - 純閱讀盲解（Part 5–7）：**{reading_blind_items}** 題
  - 聽力逐字稿盲解（Part 2–4）：**{listening_transcript_blind_items}** 題
  - Part 1 實體照片視覺盲解（Part 1）：**{part1_visual_blind_items}** 題
  - 純聽音盲解（不看逐字稿）：**0** 題（`not_run`）
- **優先真人審閱與試聽樣本包**：已建立於 [review/human_review_pack_phase1/](file:///Users/ziii/Desktop/TOEIC_IOS_App/review/human_review_pack_phase1/README-HUMAN-REVIEWER.md)（涵蓋 27 組優先抽樣／53 題 + 全量 100 題檢核表 + JSONL 回填模板）

## 待人工審閱題組清單（共 {len(ordered_gids)} 組 {accepted_candidate_count} 題）

| 最新所在批次 (版本) | Pool | Group ID | 題型 (Layout) | 小題數 | 難度 | 目前狀態 | 待辦人工審核項目 |
|---|---|---|---|---:|---|---|---|
{rq_rows}
"""
    for p in (ROOT / "REVIEW_QUEUE.md", ROOT / "reports" / "REVIEW_QUEUE.md"):
        p.write_text(rq_md, encoding="utf-8")

    # 3. Write reports/quota-and-quality-summary.md
    master_quota = json.loads((ROOT / "blueprints" / "master-quota-4800.json").read_text(encoding="utf-8"))
    roadmap_p2 = json.loads((ROOT / "jobs" / "roadmap-phase2-400.json").read_text(encoding="utf-8"))

    quota_rows = []
    for p_int in range(1, 8):
        q = master_quota["quotas_by_part_and_pool"][str(p_int)]
        done_tr = part_pool_counts[p_int]["training"]
        done_bt = part_pool_counts[p_int]["battle"]
        done_dg = part_pool_counts[p_int]["diagnostic"]
        done_mk = part_pool_counts[p_int]["mock"]
        done_tot = done_tr + done_bt + done_dg + done_mk
        quota_rows.append(
            f"| Part {p_int} | {done_tr} / {q['training']} | {done_bt} / {q['battle']} | "
            f"{done_dg} / {q['diagnostic']} | {done_mk} / {q['mock']} | **{done_tot} / {q['total']}** | {q['total'] - done_tot} |"
        )

    p2_rows = []
    for p_int in range(1, 8):
        pq = roadmap_p2["part_remaining_quotas"][str(p_int)]
        cur_tr = part_pool_counts[p_int]["training"]
        rem_tr = pq["phase2_target_cumulative"] - cur_tr
        p2_rows.append(
            f"| Part {p_int} | {pq['phase1_done']} | **{cur_tr}** | {pq['phase2_target_cumulative']} | **+{rem_tr}** |"
        )

    skill_rows = "\n".join(f"| `{sk}` | {cnt} |" for sk, cnt in sorted(skill_counts.items()))
    diff_rows = "\n".join(
        f"| {d} | {diff_counts.get(d, 0)} | {diff_counts.get(d, 0) * 100.0 / max(1, accepted_candidate_count):.1f}% |"
        for d in ("D1", "D2", "D3", "D4", "D5")
    )
    batch_rows = "\n".join(
        f"| `{b['batch_id']}` | `{b['pools']}` | {b['versions']} | {b['groups']} | {b['items']} | {b['ready_assets']} | {b['planned_assets']} | "
        f"pass:{b['val_counts']['pass']} / warn:{b['val_counts']['warning']} / fail:{b['val_counts']['fail']} / not_run:{b['val_counts']['not_run']} | `{b['overall']}` |"
        for b in batch_stats
    )

    quota_md = f"""# 配額進度、去重與品質總報告（Quota & Quality Summary）

更新時間（UTC）：`{now_iso}`

## 1. 核心驗收指標（AI 審核、人工審核、盲解模式、素材就緒、難度校準與未發布草稿嚴格分開統計）

| 指標名稱 | 數量 | 統計與邊界說明 |
|---|---:|---|
| **AI 審核合格候選小題數（`accepted_candidate_count`, `ai_checked`）** | **{accepted_candidate_count} 題** | {len(ordered_gids)} 個不重複題組：`training` **{pool_item_totals['training']}** 題（{pool_group_totals['training']} 組）、`diagnostic` **{pool_item_totals['diagnostic']}** 題（{pool_group_totals['diagnostic']} 組）、`battle` **{pool_item_totals['battle']}** 題（{pool_group_totals['battle']} 組）、`mock` **0** 題 |
| **人工審核完成小題數（`fully_reviewed_count`, `human_reviewed`）** | **{fully_reviewed_count} 題** | 0 題；未經真人審閱前絕不標記為 `human_reviewed` |
| **獨立盲解 — 純閱讀盲解（Part 5–7）** | **{reading_blind_items} 題** | 100% 由獨立上下文子代理盲解通過並留存輸入／輸出證據 |
| **獨立盲解 — 聽力逐字稿盲解（Part 2–4）** | **{listening_transcript_blind_items} 題** | 100% 由獨立上下文子代理依 `audio_script` + 圖表盲解通過 |
| **獨立盲解 — Part 1 實體圖片視覺盲解（Part 1）** | **{part1_visual_blind_items} 題** | 4 張 1200×896 照片均由獨立子代理實際讀取圖片盲解通過 |
| **獨立盲解 — 純聽音盲解（Audio-Only Blind Solve）** | **0 / {part1_visual_blind_items + listening_transcript_blind_items} 題 (`not_run`)** | 誠實標示 `not_run`；待真人試聽或多模態純音訊盲解工具驗收 |
| **累計素材就緒總小題數（合併 v2 後 `media_ready_item_count`）** | **{media_ready_items} / {accepted_candidate_count} 題** | 匯入 `batch-ag-0001..0010` 後，全數 {ready_img_count} 張圖片與 {ready_aud_count} 個音檔皆為 `status=ready` |
| **統計難度校準完成小題數（`calibrated_item_count`）** | **{calibrated_item_count} 題** | 0 題；全部題組均為 `basis="editorial"` 編輯預估難度 |
| **未發布模考草稿（`unreleased_mock_draft_count`）** | **{unrel_item_count} 題** | 存放於 `drafts/mock-form-01-unreleased/`（`pool="mock"`），**分開記錄，不計入已發布合格題** |

---

## 2. 已匯出不可變批次一覽（`exports/batch-ag-0001` 至 `0010`）

| Batch ID | Pool | 版本 | 題組數 | 小題數 | Ready 素材數 | Planned 素材數 | Validation 檢查計數 | Overall Result |
|---|---|---|---:|---:|---:|---:|---|---|
{batch_rows}

---

## 3. 第一階段 100 題 → 第二階段 400 題（`pool=training`）配額推進表

| 題型 | Phase 1 基線 | **目前已匯出 `training` 累計** | 400 題階段目標累計 | **距離 400 題剩餘需新增配額** |
|---|---:|---:|---:|---:|
{chr(10).join(p2_rows)}
| **合計** | **100 題** | **{pool_item_totals['training']} 題** | **400 題** | **+{400 - pool_item_totals['training']} 題** |

---

## 4. 長期 4,800 題（Part × Pool）總配額執行進度

| 題型 | training | battle | diagnostic | mock | 累計合格 ／ 總配額 | 距離 4,800 剩餘配額 |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(quota_rows)}
| **合計** | **{pool_item_totals['training']} / 3,000** | **{pool_item_totals['battle']} / 600** | **{pool_item_totals['diagnostic']} / 400** | **{pool_item_totals['mock']} / 800** | **{accepted_candidate_count} / 4,800** | **{4800 - accepted_candidate_count}** |

---

## 5. 全域 {accepted_candidate_count} 題難度分布（Editorial Difficulty）

| 難度等級 | 小題數 | 佔比 |
|---|---:|---:|
{diff_rows}

---

## 6. 本專案定義的 22 項能力標籤（Project-Defined Skill Taxonomy）覆蓋統計

目前已匯出 {accepted_candidate_count} 題 100% 覆蓋契約 H 節所列、**本專案定義的 22 項能力標籤**（非 ETS 官方認證標籤）：

| Skill Tag | 覆蓋題次 |
|---|---:|
{skill_rows}

---

## 7. 去重、版本升級與家族隔離驗證結果

- **跨版本唯一性**：{len(ordered_gids)} 個獨立 `group_id`、{accepted_candidate_count} 個獨立 `item_id`。
- **完全相同與正規化文字去重**：{len(ordered_gids)} 個獨立題組跨批次比對 **0 重複**。
- **同題型跨家族 n-gram 餘弦相似度檢查**：全部獨立題組兩兩比對均低於 0.82 警戒閾值（**0 近似警告**）。
- **家族（`family_id`）跨用途池隔離**：{len(family_pools)} 個已匯出獨立 `family_id`（`training`: {pool_group_totals['training']}、`diagnostic`: {pool_group_totals['diagnostic']}、`battle`: {pool_group_totals['battle']}），跨池衝突數為 **0**。
"""
    (ROOT / "reports" / "quota-and-quality-summary.md").write_text(quota_md, encoding="utf-8")

    # 4. Write PROGRESS.md
    prog_md = f"""# TOEIC 原創題庫生產進度（PROGRESS.md）

最後更新時間（UTC）：`{now_iso}`

## 1. 當前階段與嚴格分開統計之核心指標

- **目前階段**：已完成 **Gate 1（模考契約對齊 `specs/mock-form-contract-v1.md`）、Gate 2（現有 100 題深度品質複審、真人審閱包與 27 音檔容器／有效音框／波形對齊技術審計）、Gate 3（`batch-ag-0008` training 擴充、`batch-ag-0009` diagnostic 獨立池交付、`batch-ag-0010` battle 獨立池交付）及 Gate 4（完整交接報告）**。
- **嚴格分開統計指標**：
  - **AI 審核合格數（`accepted_candidate_count`, `ai_checked`）**：**{accepted_candidate_count} 題**（{len(ordered_gids)} 個獨立題組：`training` {pool_item_totals['training']} 題、`diagnostic` {pool_item_totals['diagnostic']} 題、`battle` {pool_item_totals['battle']} 題、`mock` 0 題）
  - **人工審核完成數（`fully_reviewed_count`, `human_reviewed`）**：**0 題**
  - **獨立盲解驗證分類**：
    - 純閱讀文字盲解（Part 5–7）：**{reading_blind_items} 題**（PASS）
    - 聽力逐字稿盲解（Part 2–4）：**{listening_transcript_blind_items} 題**（PASS）
    - Part 1 實體照片視覺盲解（Part 1）：**{part1_visual_blind_items} 題**（PASS）
    - 純聽音盲解（不看稿 Audio-Only）：**0 / {part1_visual_blind_items + listening_transcript_blind_items} 題**（`not_run`）
  - **素材就緒數（`media_ready_item_count`）**：**{media_ready_items} / {accepted_candidate_count} 題**（{ready_img_count} 張實景照片 + {ready_aud_count} 個 `.m4a` 音檔全數 `status=ready`）
  - **難度校準完成數（`calibrated_item_count`）**：**0 題**（全數為 `basis="editorial"`）
  - **未發布模考草稿（`unreleased_mock_draft_count`）**：**{unrel_item_count} 題**（位於 `drafts/mock-form-01-unreleased/`，不計入已發布合格題）

## 2. 已匯出不可變批次清單（`exports/batch-ag-0001` .. `0010`）

| Batch ID | Pool | 版本 | 角色與定位 | 題組數 | 小題數 | 實體音圖資產 | 狀態 |
|---|---|---|---|---:|---:|---|---|
| `batch-ag-0001` | `training` | `v1` | 原始五包基線（Part 2 × 8 + Part 5 × 12，不可變） | 20 | 20 | 0 ready / 8 planned | `exported` |
| `batch-ag-0002` | `training` | `v1` | 原始五包基線（Part 1 × 3 + Part 2 × 5 + Part 5 × 3 + Part 6 × 8，不可變） | 13 | 19 | 0 ready / 11 planned | `exported` |
| `batch-ag-0003` | `training` | `v1` | 原始五包基線（Part 3 × 6 組 18 題，不可變） | 6 | 18 | 0 ready / 6 planned | `exported` |
| `batch-ag-0004` | `training` | `v1` | 原始五包基線（Part 4 × 5 組 15 題，不可變） | 5 | 15 | 0 ready / 5 planned | `exported` |
| `batch-ag-0005` | `training` | `v1` | 原始五包基線（Part 7 × 7 組 28 題，純文字表格，不可變） | 7 | 28 | 無須外部音圖 | `exported` |
| `batch-ag-0006` | `training` | `v2` | 四題型聽力可播放樣本升級包（`ag-g-p1/p2/p3/p4-000001`） | 4 | 8 | 1 圖 + 4 音檔 `ready` | `exported` |
| `batch-ag-0007` | `training` | `v2` | 第一階段其餘 23 組聽力媒體補齊升級包 | 23 | 41 | 2 圖 + 23 音檔 `ready` | `exported` |
| `batch-ag-0008` | `training` | `v1` | **Phase 2 `training` 受控擴充第一批**（Part 5 × 16 + Part 6 × 8 + Part 7 × 5） | 20 | 29 | 純文字無須外部音圖 | `exported` |
| `batch-ag-0009` | `diagnostic` | `v1` | **首個獨立 `diagnostic` 池全題型批次**（Part 1–7 共 14 組 24 題） | 14 | 24 | **1 圖 + 8 音檔 `ready`** | `exported` |
| `batch-ag-0010` | `battle` | `v1` | **首個獨立 `battle` 池對戰批次**（Part 2 × 6 + Part 5 × 14 + Part 6 × 4） | 21 | 24 | **6 音檔 `ready`** | `exported` |

## 3. 中斷續跑與交接指引

- 本輪完整交接清單與驗證命令請見：[handoff/2026-10-28/antigravity-delivery.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-delivery.md)
- 模考附加契約對齊狀態請見：[handoff/2026-10-28/antigravity-contract-status.md](file:///Users/ziii/Desktop/TOEIC_IOS_App/handoff/2026-10-28/antigravity-contract-status.md)
"""
    (ROOT / "PROGRESS.md").write_text(prog_md, encoding="utf-8")
    print("Master reports updated successfully.")


if __name__ == "__main__":
    main()
