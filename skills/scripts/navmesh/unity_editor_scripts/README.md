# NavMesh 批量导出 — Unity 编辑器侧

本目录放 Unity Editor C# 脚本,负责从 Unity 工程把 NavMesh 导成 JSON。

## 安装(一次性)

1. 打开 Unity 工程:`D:\meishu`
2. 在 Project 窗口的 `Assets/` 下创建 `Editor` 文件夹(如已有则跳过)
3. 把 `NavMeshExporter.cs` **复制**到 `D:\meishu\Assets\Editor\NavMeshExporter.cs`
4. Unity 会自动编译,等下方 Console 没报错即可
5. 菜单栏出现 `Tools > NavMesh > ...`

## 首次配置(一次性)

点击 `Tools > NavMesh > Configure Repo Path...`,选择仓库根目录:

```
C:\Users\Hetao\Desktop\公司
```

(该目录下必须有 `scripts/navmesh/scene_index.json`,不然会报错)

路径记在 Unity 的 `EditorPrefs` 里,重启 Unity 后仍有效。

## 菜单说明

| 菜单项 | 作用 |
|---|---|
| `Configure Repo Path...` | 设置仓库根(首次使用必配) |
| `Export Current Scene` | 导出当前打开的场景,需要你输入对应 AssetId |
| `Export By AssetId...` | 按 AssetId 打开场景并导出(单个) |
| `Export All From Index` | **批量导全部 160 个**(已有缓存跳过) |
| `Export All (Force Re-export)` | 强制重导全部(清缓存效果) |
| `Open Cache Folder` | 打开导出结果目录 |

## 推荐流程(第一次)

1. `Configure Repo Path...` 指向仓库根
2. `Export Current Scene` 先随便挑一个场景测一下,确认能导出 JSON 到 `scripts/navmesh/navmesh_cache/<AssetId>.json`
3. `Export All From Index` 批量导全部(会弹确认框,确认后开始,有进度条,160 个预计 5-15 分钟)

## 输出

- `scripts/navmesh/navmesh_cache/<AssetId>.json` — 每个场景一份
- `scripts/navmesh/navmesh_cache/_summary.json` — 本次批量结果摘要(ok/failed 列表)

## 单个 JSON 字段

```json
{
  "asset_id": 12836,
  "name": "l1-02-02-c",
  "unity_file": "l1-02-02-c.unity",
  "unity_path": "D:\\meishu\\...",
  "exported_at": "2026-04-24T...Z",
  "unity_version": "2021.3.11f1c2",
  "export_version": "1.0.0",
  "agent": {
    "type_id": 0,
    "radius": 0.5,
    "height": 2.0,
    "step_height": 0.4,
    "slope": 45.0
  },
  "bounds": { "min": [x,y,z], "max": [x,y,z] },
  "navmesh": {
    "vert_count": N,
    "tri_count": M,
    "vertices": [[x,y,z], ...],
    "triangles": [[i,j,k], ...],
    "areas": [0, 0, 2, ...]
  },
  "areas_legend": { "0": "Walkable", "1": "Not Walkable", ... }
}
```

## 注意事项

- 批量导出会**依次 Single 模式打开每个场景**,当前场景的未保存修改会丢失。脚本会在开始前提醒你先保存
- 批量过程中可以点 Unity 进度条的 Cancel 中止,已导的不会丢
- 某些场景如果 NavMesh 没烘(`vertices=0`),脚本仍会写出一个空 navmesh 的 JSON 并留日志告警
- 导出用的是 `UnityEngine.AI.NavMesh.CalculateTriangulation()`,拿的是当前场景加载的 NavMeshData 的三角剖分(可行走面)
