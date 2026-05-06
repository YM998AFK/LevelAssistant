/*
 * NavMeshExporter.cs
 *
 * 盘古3D 项目 NavMesh 批量导出工具(Unity Editor Only)。
 *
 * 安装:把本文件复制到 `<UnityProject>/Assets/Editor/NavMeshExporter.cs`
 *       (Editor 文件夹不存在就新建,Unity 会自动识别)
 *
 * 菜单位置:Unity 菜单栏 > Tools > NavMesh
 *   - Configure Repo Path...    首次使用先设置仓库根目录(含 scripts/navmesh/ 的那个)
 *   - Export Current Scene      导出当前已打开场景的 NavMesh(快速测试)
 *   - Export By AssetId...      输入 AssetId,从 scene_index.json 定位并导出
 *   - Export All From Index     批量(默认跳过已缓存的)
 *   - Export All (Force)        批量强制重导
 *   - Open Cache Folder         打开缓存目录查看结果
 *
 * 输出:<Repo>/scripts/navmesh/navmesh_cache/<AssetId>.json
 *       <Repo>/scripts/navmesh/navmesh_cache/_summary.json
 *
 * JSON 字段:
 *   asset_id / name / unity_file / unity_path
 *   exported_at / unity_version / export_version
 *   agent {radius, height, step_height, slope, type_id}
 *   bounds {min[3], max[3]}
 *   navmesh {vert_count, tri_count, vertices[[x,y,z]], triangles[[i,j,k]], areas[]}
 *   areas_legend {index: name}
 *
 * 坐标系:Unity 左手 Y-up,直接导出,单位米。
 */

#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

public static class NavMeshExporter
{
    private const string EXPORT_VERSION = "1.0.0";
    private const string PREF_REPO_PATH = "NavMeshExporter.RepoPath";
    private const string INDEX_REL = "scripts/navmesh/scene_index.json";
    private const string CACHE_REL = "scripts/navmesh/navmesh_cache";

    // ─────────────────────────────────────────────────────────────
    // Menu: Configure Repo Path
    // ─────────────────────────────────────────────────────────────
    [MenuItem("Tools/NavMesh/Configure Repo Path...", priority = 0)]
    public static void ConfigureRepoPath()
    {
        string current = EditorPrefs.GetString(PREF_REPO_PATH, "");
        string picked = EditorUtility.OpenFolderPanel(
            "选择仓库根目录(包含 scripts/navmesh/ 的文件夹)",
            string.IsNullOrEmpty(current) ? Directory.GetCurrentDirectory() : current,
            "");
        if (string.IsNullOrEmpty(picked)) return;

        string indexPath = Path.Combine(picked, INDEX_REL.Replace('/', Path.DirectorySeparatorChar));
        if (!File.Exists(indexPath))
        {
            EditorUtility.DisplayDialog("目录不对",
                "该目录下找不到 " + INDEX_REL + "\n请先运行 build_scene_index.py 建立索引。",
                "OK");
            return;
        }

        EditorPrefs.SetString(PREF_REPO_PATH, picked);
        Debug.Log("[NavMeshExporter] Repo path saved: " + picked);
        EditorUtility.DisplayDialog("已保存", "仓库根目录:\n" + picked, "OK");
    }

    private static string GetRepoPath(bool promptIfMissing = true)
    {
        string cli = CliArg("-RepoPath");
        if (!string.IsNullOrEmpty(cli) && Directory.Exists(cli))
        {
            string idx = Path.Combine(cli, INDEX_REL.Replace('/', Path.DirectorySeparatorChar));
            if (File.Exists(idx)) return cli;
        }

        string p = EditorPrefs.GetString(PREF_REPO_PATH, "");
        if (!string.IsNullOrEmpty(p) && Directory.Exists(p))
        {
            string idx = Path.Combine(p, INDEX_REL.Replace('/', Path.DirectorySeparatorChar));
            if (File.Exists(idx)) return p;
        }
        if (promptIfMissing && !Application.isBatchMode)
            EditorUtility.DisplayDialog("请先配置", "请先执行 Tools/NavMesh/Configure Repo Path...", "OK");
        return null;
    }

    // ─────────────────────────────────────────────────────────────
    // CLI helpers (供 batch mode 读命令行参数)
    // ─────────────────────────────────────────────────────────────
    private static string CliArg(string flag)
    {
        var args = Environment.GetCommandLineArgs();
        for (int i = 0; i < args.Length - 1; i++)
            if (args[i] == flag) return args[i + 1];
        return null;
    }
    private static bool CliFlag(string flag)
    {
        var args = Environment.GetCommandLineArgs();
        foreach (var a in args) if (a == flag) return true;
        return false;
    }

    private static string GetCacheDir()
    {
        string repo = GetRepoPath();
        if (repo == null) return null;
        string dir = Path.Combine(repo, CACHE_REL.Replace('/', Path.DirectorySeparatorChar));
        Directory.CreateDirectory(dir);
        return dir;
    }

    // ─────────────────────────────────────────────────────────────
    // Menu: Open Cache Folder
    // ─────────────────────────────────────────────────────────────
    [MenuItem("Tools/NavMesh/Open Cache Folder", priority = 100)]
    public static void OpenCacheFolder()
    {
        string dir = GetCacheDir();
        if (dir == null) return;
        EditorUtility.RevealInFinder(dir);
    }

    // ─────────────────────────────────────────────────────────────
    // Menu: Export Current Scene
    // ─────────────────────────────────────────────────────────────
    [MenuItem("Tools/NavMesh/Export Current Scene", priority = 20)]
    public static void ExportCurrentScene()
    {
        string cacheDir = GetCacheDir();
        if (cacheDir == null) return;

        var active = EditorSceneManager.GetActiveScene();
        if (string.IsNullOrEmpty(active.path))
        {
            EditorUtility.DisplayDialog("无场景", "当前没有已保存的活动场景。", "OK");
            return;
        }

        int assetId = PromptAssetId("输入此场景对应的 AssetId(可在 scene_index.json 查)");
        if (assetId <= 0) return;

        var entry = FindEntryByAssetId(assetId);
        if (entry == null)
        {
            if (!EditorUtility.DisplayDialog("AssetId 不在索引",
                "AssetId " + assetId + " 在 scene_index.json 中找不到,仍要导出吗?",
                "继续", "取消"))
                return;
            entry = new SceneEntry
            {
                AssetId = assetId,
                Name = active.name,
                UnityFile = Path.GetFileName(active.path),
                UnityAbspath = Path.GetFullPath(active.path)
            };
        }

        try
        {
            string outPath = ExportOne(entry, cacheDir, out string msg);
            Debug.Log("[NavMeshExporter] " + msg);
            EditorUtility.DisplayDialog("完成", msg + "\n\n" + outPath, "OK");
        }
        catch (Exception e)
        {
            Debug.LogError("[NavMeshExporter] Export failed: " + e);
            EditorUtility.DisplayDialog("失败", e.Message, "OK");
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Menu: Export By AssetId
    // ─────────────────────────────────────────────────────────────
    [MenuItem("Tools/NavMesh/Export By AssetId...", priority = 21)]
    public static void ExportByAssetId()
    {
        string cacheDir = GetCacheDir();
        if (cacheDir == null) return;

        int assetId = PromptAssetId("输入要导出的 AssetId");
        if (assetId <= 0) return;

        var entry = FindEntryByAssetId(assetId);
        if (entry == null)
        {
            EditorUtility.DisplayDialog("找不到", "AssetId " + assetId + " 不在 scene_index.json 中", "OK");
            return;
        }

        if (!PromptOpenSceneConfirm(new List<SceneEntry> { entry })) return;

        try
        {
            OpenSceneBlocking(entry);
            string outPath = ExportOne(entry, cacheDir, out string msg);
            Debug.Log("[NavMeshExporter] " + msg);
            EditorUtility.DisplayDialog("完成", msg + "\n\n" + outPath, "OK");
        }
        catch (Exception e)
        {
            Debug.LogError("[NavMeshExporter] Export failed: " + e);
            EditorUtility.DisplayDialog("失败", e.Message, "OK");
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Menu: Export All From Index
    // ─────────────────────────────────────────────────────────────
    [MenuItem("Tools/NavMesh/Export All From Index", priority = 30)]
    public static void ExportAllFromIndex() => ExportAllImpl(force: false);

    [MenuItem("Tools/NavMesh/Export All (Force Re-export)", priority = 31)]
    public static void ExportAllForce() => ExportAllImpl(force: true);

    // ─────────────────────────────────────────────────────────────
    // Batch mode entry (供命令行 -executeMethod 调用)
    //
    // 用法:
    //   Unity.exe -batchmode -nographics -projectPath <path> ^
    //     -executeMethod NavMeshExporter.BatchExportAll ^
    //     -RepoPath "C:\path\to\repo" ^
    //     [-BatchAssetId 12836]   (可选: 只导一个,便于测试)
    //     [-BatchForce]            (可选: 强制覆盖已有 cache)
    //     -logFile <path> -quit
    // ─────────────────────────────────────────────────────────────
    public static void BatchExportAll()
    {
        int exitCode = 0;
        try
        {
            string repo = GetRepoPath(promptIfMissing: false);
            if (repo == null)
            {
                Debug.LogError("[NavMeshExporter/Batch] 未找到 repo path,请传 -RepoPath <dir>");
                EditorApplication.Exit(2);
                return;
            }
            string cacheDir = Path.Combine(repo, CACHE_REL.Replace('/', Path.DirectorySeparatorChar));
            Directory.CreateDirectory(cacheDir);
            Debug.Log("[NavMeshExporter/Batch] RepoPath = " + repo);
            Debug.Log("[NavMeshExporter/Batch] CacheDir = " + cacheDir);

            bool force = CliFlag("-BatchForce");
            string onlyIdStr = CliArg("-BatchAssetId");
            int onlyId = 0;
            if (!string.IsNullOrEmpty(onlyIdStr))
                int.TryParse(onlyIdStr, NumberStyles.Integer, CultureInfo.InvariantCulture, out onlyId);

            var entries = LoadAllEntriesWithNavMesh();
            if (entries == null || entries.Count == 0)
            {
                Debug.LogError("[NavMeshExporter/Batch] 索引里没有带 NavMesh 的场景");
                EditorApplication.Exit(3);
                return;
            }

            if (onlyId > 0)
            {
                entries = entries.FindAll(e => e.AssetId == onlyId);
                if (entries.Count == 0)
                {
                    Debug.LogError("[NavMeshExporter/Batch] 找不到 AssetId=" + onlyId);
                    EditorApplication.Exit(4);
                    return;
                }
                Debug.Log("[NavMeshExporter/Batch] 只跑单场景: AssetId=" + onlyId);
            }

            if (!force)
            {
                int before = entries.Count;
                entries.RemoveAll(e => File.Exists(Path.Combine(cacheDir, e.AssetId + ".json")));
                int skipped = before - entries.Count;
                if (skipped > 0)
                    Debug.Log("[NavMeshExporter/Batch] 跳过已缓存: " + skipped + " 个");
            }

            if (entries.Count == 0)
            {
                Debug.Log("[NavMeshExporter/Batch] 没有待导的场景 (全部已缓存)");
                EditorApplication.Exit(0);
                return;
            }

            int total = entries.Count;
            int ok = 0, failed = 0;
            var summary = new List<Dictionary<string, object>>();
            var started = DateTime.UtcNow;

            for (int i = 0; i < total; i++)
            {
                var entry = entries[i];
                Debug.Log($"[NavMeshExporter/Batch] [{i + 1}/{total}] {entry.AssetId}  {entry.Name}  ({entry.UnityFile})");
                try
                {
                    OpenSceneBlocking(entry);
                    string outPath = ExportOne(entry, cacheDir, out string msg);
                    Debug.Log($"[NavMeshExporter/Batch]   OK  {msg}  ->  {outPath}");
                    summary.Add(BuildSummaryItem(entry, outPath, "ok", null));
                    ok++;
                }
                catch (Exception e)
                {
                    Debug.LogError($"[NavMeshExporter/Batch]   FAIL  {e.Message}");
                    summary.Add(BuildSummaryItem(entry, null, "failed", e.Message));
                    failed++;
                }
            }

            WriteSummary(cacheDir, summary, started, ok, failed, 0);

            Debug.Log("[NavMeshExporter/Batch] ========== DONE ==========");
            Debug.Log($"[NavMeshExporter/Batch] OK={ok}  FAIL={failed}  total={total}");
            exitCode = failed > 0 ? 5 : 0;
        }
        catch (Exception e)
        {
            Debug.LogError("[NavMeshExporter/Batch] 未捕获异常: " + e);
            exitCode = 9;
        }
        finally
        {
            EditorApplication.Exit(exitCode);
        }
    }

    private static void ExportAllImpl(bool force)
    {
        string cacheDir = GetCacheDir();
        if (cacheDir == null) return;

        List<SceneEntry> entries = LoadAllEntriesWithNavMesh();
        if (entries == null || entries.Count == 0)
        {
            EditorUtility.DisplayDialog("无可导", "scene_index.json 里没有带 NavMesh 的场景", "OK");
            return;
        }

        if (!force)
            entries.RemoveAll(e =>
                File.Exists(Path.Combine(cacheDir, e.AssetId + ".json")));

        if (entries.Count == 0)
        {
            EditorUtility.DisplayDialog("全部已缓存",
                "所有场景都已经导出过,若要重新导出请使用 Export All (Force)。", "OK");
            return;
        }

        if (!PromptOpenSceneConfirm(entries)) return;

        int total = entries.Count;
        int ok = 0, skipped = 0, failed = 0;
        var errors = new List<string>();
        var summary = new List<Dictionary<string, object>>();
        var started = DateTime.UtcNow;

        for (int i = 0; i < total; i++)
        {
            var entry = entries[i];
            float progress = (float)i / total;
            if (EditorUtility.DisplayCancelableProgressBar(
                "Exporting NavMesh",
                $"[{i + 1}/{total}] {entry.AssetId} {entry.Name}",
                progress))
            {
                errors.Add("用户取消,剩余 " + (total - i) + " 个未导");
                break;
            }

            try
            {
                OpenSceneBlocking(entry);
                string outPath = ExportOne(entry, cacheDir, out string msg);
                Debug.Log($"[NavMeshExporter] OK  {entry.AssetId} {entry.Name} → {msg}");
                var item = BuildSummaryItem(entry, outPath, "ok", null);
                summary.Add(item);
                ok++;
            }
            catch (Exception e)
            {
                Debug.LogError($"[NavMeshExporter] FAIL {entry.AssetId} {entry.Name}: {e.Message}");
                errors.Add($"{entry.AssetId} {entry.Name}: {e.Message}");
                summary.Add(BuildSummaryItem(entry, null, "failed", e.Message));
                failed++;
            }
        }

        EditorUtility.ClearProgressBar();

        WriteSummary(cacheDir, summary, started, ok, failed, skipped);

        string info = $"完成: OK={ok}  FAIL={failed}\n缓存目录: {cacheDir}";
        if (errors.Count > 0)
            info += "\n\n错误前 5 条:\n" + string.Join("\n", errors.GetRange(0, Math.Min(5, errors.Count)));
        EditorUtility.DisplayDialog("NavMesh 批量导出完成", info, "OK");
    }

    // ─────────────────────────────────────────────────────────────
    // Core: Export one scene -> JSON
    // ─────────────────────────────────────────────────────────────
    private static string ExportOne(SceneEntry entry, string cacheDir, out string message)
    {
        NavMeshTriangulation tri = NavMesh.CalculateTriangulation();
        int vertCount = tri.vertices != null ? tri.vertices.Length : 0;
        int idxCount = tri.indices != null ? tri.indices.Length : 0;
        int triCount = idxCount / 3;

        if (vertCount == 0 || triCount == 0)
        {
            message = $"WARNING: vertices={vertCount} triangles={triCount},但仍写出空 navmesh JSON";
        }
        else
        {
            message = $"vertices={vertCount} triangles={triCount}";
        }

        // agent settings (取 index 0,默认 agent)
        NavMeshBuildSettings settings = NavMesh.GetSettingsByIndex(0);
        int agentTypeId = settings.agentTypeID;
        float agentRadius = settings.agentRadius;
        float agentHeight = settings.agentHeight;
        float agentClimb = settings.agentClimb;
        float agentSlope = settings.agentSlope;

        // bounds
        Vector3 bMin = Vector3.zero, bMax = Vector3.zero;
        if (vertCount > 0)
        {
            bMin = tri.vertices[0];
            bMax = tri.vertices[0];
            for (int i = 1; i < vertCount; i++)
            {
                var v = tri.vertices[i];
                if (v.x < bMin.x) bMin.x = v.x; if (v.x > bMax.x) bMax.x = v.x;
                if (v.y < bMin.y) bMin.y = v.y; if (v.y > bMax.y) bMax.y = v.y;
                if (v.z < bMin.z) bMin.z = v.z; if (v.z > bMax.z) bMax.z = v.z;
            }
        }

        // areas
        var areas = new int[triCount];
        if (tri.areas != null && tri.areas.Length == triCount)
            Array.Copy(tri.areas, areas, triCount);

        // areas legend
        string[] areaNames = GameObjectUtility.GetNavMeshAreaNames();

        // JSON 手写(避免 JsonUtility 嵌套数组限制)
        var sb = new StringBuilder(64 * 1024);
        sb.Append('{');
        AppendKV(sb, "asset_id", entry.AssetId); sb.Append(',');
        AppendKVStr(sb, "name", entry.Name); sb.Append(',');
        AppendKVStr(sb, "unity_file", entry.UnityFile); sb.Append(',');
        AppendKVStr(sb, "unity_path", entry.UnityAbspath ?? ""); sb.Append(',');
        AppendKVStr(sb, "exported_at", DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture)); sb.Append(',');
        AppendKVStr(sb, "unity_version", Application.unityVersion); sb.Append(',');
        AppendKVStr(sb, "export_version", EXPORT_VERSION); sb.Append(',');

        // agent
        sb.Append("\"agent\":{");
        AppendKV(sb, "type_id", agentTypeId); sb.Append(',');
        AppendKVF(sb, "radius", agentRadius); sb.Append(',');
        AppendKVF(sb, "height", agentHeight); sb.Append(',');
        AppendKVF(sb, "step_height", agentClimb); sb.Append(',');
        AppendKVF(sb, "slope", agentSlope);
        sb.Append("},");

        // bounds
        sb.Append("\"bounds\":{\"min\":");
        AppendVec3(sb, bMin);
        sb.Append(",\"max\":");
        AppendVec3(sb, bMax);
        sb.Append("},");

        // navmesh
        sb.Append("\"navmesh\":{");
        AppendKV(sb, "vert_count", vertCount); sb.Append(',');
        AppendKV(sb, "tri_count", triCount); sb.Append(',');
        sb.Append("\"vertices\":[");
        for (int i = 0; i < vertCount; i++)
        {
            if (i > 0) sb.Append(',');
            AppendVec3(sb, tri.vertices[i]);
        }
        sb.Append("],\"triangles\":[");
        for (int t = 0; t < triCount; t++)
        {
            if (t > 0) sb.Append(',');
            int i0 = tri.indices[t * 3 + 0];
            int i1 = tri.indices[t * 3 + 1];
            int i2 = tri.indices[t * 3 + 2];
            sb.Append('[').Append(i0).Append(',').Append(i1).Append(',').Append(i2).Append(']');
        }
        sb.Append("],\"areas\":[");
        for (int i = 0; i < areas.Length; i++)
        {
            if (i > 0) sb.Append(',');
            sb.Append(areas[i]);
        }
        sb.Append("]},");

        // areas legend
        sb.Append("\"areas_legend\":{");
        for (int i = 0; i < areaNames.Length; i++)
        {
            if (i > 0) sb.Append(',');
            sb.Append('"').Append(i).Append("\":");
            AppendStr(sb, areaNames[i]);
        }
        sb.Append('}');

        sb.Append('}');

        string outPath = Path.Combine(cacheDir, entry.AssetId + ".json");
        File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false));
        return outPath;
    }

    // ─────────────────────────────────────────────────────────────
    // Scene load helper
    // ─────────────────────────────────────────────────────────────
    private static void OpenSceneBlocking(SceneEntry entry)
    {
        string unityPath = entry.UnityAbspath;
        if (string.IsNullOrEmpty(unityPath) || !File.Exists(unityPath))
            throw new FileNotFoundException("找不到 .unity 文件: " + unityPath);

        // Unity 要求场景路径以 Assets/ 开头(相对 project)。把绝对路径转成项目相对路径。
        string projectRoot = Path.GetDirectoryName(Application.dataPath); // = <Unity Project>
        string rel = MakeRelative(projectRoot, unityPath);
        if (rel == null)
            throw new InvalidOperationException("场景文件不在当前 Unity 工程下: " + unityPath);

        EditorSceneManager.OpenScene(rel, OpenSceneMode.Single);
    }

    private static string MakeRelative(string root, string abs)
    {
        root = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
            + Path.DirectorySeparatorChar;
        abs = Path.GetFullPath(abs);
        if (!abs.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            return null;
        return abs.Substring(root.Length).Replace('\\', '/');
    }

    // ─────────────────────────────────────────────────────────────
    // Index loading (minimal JSON reader for scene_index.json)
    // ─────────────────────────────────────────────────────────────
    private class SceneEntry
    {
        public int AssetId;
        public string Name;
        public string UnityFile;
        public string UnityAbspath;
        public string NavMeshAbspath;
        public bool HasNavMesh;
        public string Category;
    }

    private static List<SceneEntry> _cachedEntries;

    private static List<SceneEntry> LoadAllEntries()
    {
        if (_cachedEntries != null) return _cachedEntries;
        string repo = GetRepoPath();
        if (repo == null) return null;
        string idx = Path.Combine(repo, INDEX_REL.Replace('/', Path.DirectorySeparatorChar));
        string text = File.ReadAllText(idx, Encoding.UTF8);

        var list = new List<SceneEntry>();
        // 用 Unity 内置 JSON 解析 _meta + scenes 结构:
        // JsonUtility 不支持 Dictionary,所以用最小正则切出每条 scene 记录。
        int scenesStart = text.IndexOf("\"scenes\"");
        if (scenesStart < 0) throw new Exception("scene_index.json 缺少 \"scenes\" 字段");
        int brace = text.IndexOf('{', scenesStart);
        int depth = 0;
        int i = brace;
        for (; i < text.Length; i++)
        {
            if (text[i] == '{') depth++;
            else if (text[i] == '}') { depth--; if (depth == 0) break; }
        }
        if (depth != 0) throw new Exception("scene_index.json 解析失败:括号不配对");
        string scenesBody = text.Substring(brace + 1, i - brace - 1);

        // 逐条对象解析(按顶层 { ... } 分块)
        int p = 0;
        while (p < scenesBody.Length)
        {
            while (p < scenesBody.Length && scenesBody[p] != '{') p++;
            if (p >= scenesBody.Length) break;
            int objStart = p;
            int d = 0;
            for (; p < scenesBody.Length; p++)
            {
                if (scenesBody[p] == '{') d++;
                else if (scenesBody[p] == '}') { d--; if (d == 0) { p++; break; } }
            }
            string obj = scenesBody.Substring(objStart, p - objStart);
            var e = ParseSceneEntry(obj);
            if (e != null) list.Add(e);
        }

        _cachedEntries = list;
        return list;
    }

    private static List<SceneEntry> LoadAllEntriesWithNavMesh()
    {
        var all = LoadAllEntries();
        if (all == null) return null;
        var res = new List<SceneEntry>();
        foreach (var e in all)
            if (e.HasNavMesh && !string.IsNullOrEmpty(e.UnityAbspath)) res.Add(e);
        return res;
    }

    private static SceneEntry FindEntryByAssetId(int id)
    {
        var all = LoadAllEntries();
        if (all == null) return null;
        foreach (var e in all) if (e.AssetId == id) return e;
        return null;
    }

    private static SceneEntry ParseSceneEntry(string obj)
    {
        int ExtractInt(string key, int fallback = 0)
        {
            string v = ExtractRaw(obj, key);
            if (string.IsNullOrEmpty(v)) return fallback;
            int.TryParse(v, NumberStyles.Integer, CultureInfo.InvariantCulture, out int r);
            return r;
        }
        string ExtractStr(string key) => ExtractStringField(obj, key);
        bool ExtractBool(string key)
        {
            string v = ExtractRaw(obj, key);
            return v == "true";
        }
        var e = new SceneEntry
        {
            AssetId = ExtractInt("asset_id"),
            Name = ExtractStr("name"),
            Category = ExtractStr("category"),
            UnityFile = ExtractStr("unity_file"),
            UnityAbspath = ExtractStr("unity_abspath"),
            NavMeshAbspath = ExtractStr("navmesh_abspath"),
            HasNavMesh = ExtractBool("has_navmesh"),
        };
        if (e.AssetId <= 0) return null;
        return e;
    }

    private static string ExtractStringField(string obj, string key)
    {
        string pat = "\"" + key + "\"";
        int k = obj.IndexOf(pat);
        if (k < 0) return null;
        int colon = obj.IndexOf(':', k);
        if (colon < 0) return null;
        int i = colon + 1;
        while (i < obj.Length && (obj[i] == ' ' || obj[i] == '\t' || obj[i] == '\n' || obj[i] == '\r')) i++;
        if (i >= obj.Length) return null;
        if (obj[i] == 'n') return null; // null
        if (obj[i] != '"') return null;
        i++;
        var sb = new StringBuilder();
        while (i < obj.Length)
        {
            char c = obj[i];
            if (c == '\\' && i + 1 < obj.Length)
            {
                char n = obj[i + 1];
                if (n == '"') sb.Append('"');
                else if (n == '\\') sb.Append('\\');
                else if (n == '/') sb.Append('/');
                else if (n == 'n') sb.Append('\n');
                else if (n == 't') sb.Append('\t');
                else if (n == 'r') sb.Append('\r');
                else if (n == 'u' && i + 5 < obj.Length)
                {
                    string hex = obj.Substring(i + 2, 4);
                    sb.Append((char)Convert.ToInt32(hex, 16));
                    i += 6; continue;
                }
                else sb.Append(n);
                i += 2; continue;
            }
            if (c == '"') break;
            sb.Append(c);
            i++;
        }
        return sb.ToString();
    }

    private static string ExtractRaw(string obj, string key)
    {
        string pat = "\"" + key + "\"";
        int k = obj.IndexOf(pat);
        if (k < 0) return null;
        int colon = obj.IndexOf(':', k);
        if (colon < 0) return null;
        int i = colon + 1;
        while (i < obj.Length && (obj[i] == ' ' || obj[i] == '\t')) i++;
        int j = i;
        while (j < obj.Length && obj[j] != ',' && obj[j] != '\n' && obj[j] != '}') j++;
        return obj.Substring(i, j - i).Trim();
    }

    // ─────────────────────────────────────────────────────────────
    // Summary writer
    // ─────────────────────────────────────────────────────────────
    private static Dictionary<string, object> BuildSummaryItem(SceneEntry e, string outPath, string status, string error)
    {
        return new Dictionary<string, object>
        {
            {"asset_id", e.AssetId},
            {"name", e.Name},
            {"status", status},
            {"output", outPath},
            {"error", error},
        };
    }

    private static void WriteSummary(string cacheDir, List<Dictionary<string, object>> items,
        DateTime started, int ok, int failed, int skipped)
    {
        var sb = new StringBuilder();
        sb.Append('{');
        AppendKVStr(sb, "started_at", started.ToString("o", CultureInfo.InvariantCulture)); sb.Append(',');
        AppendKVStr(sb, "finished_at", DateTime.UtcNow.ToString("o", CultureInfo.InvariantCulture)); sb.Append(',');
        AppendKV(sb, "ok", ok); sb.Append(',');
        AppendKV(sb, "failed", failed); sb.Append(',');
        AppendKV(sb, "skipped", skipped); sb.Append(',');
        sb.Append("\"items\":[");
        for (int i = 0; i < items.Count; i++)
        {
            if (i > 0) sb.Append(',');
            var it = items[i];
            sb.Append('{');
            AppendKV(sb, "asset_id", (int)it["asset_id"]); sb.Append(',');
            AppendKVStr(sb, "name", (string)it["name"]); sb.Append(',');
            AppendKVStr(sb, "status", (string)it["status"]); sb.Append(',');
            AppendKVStr(sb, "output", (string)(it["output"] ?? "")); sb.Append(',');
            AppendKVStr(sb, "error", (string)(it["error"] ?? ""));
            sb.Append('}');
        }
        sb.Append("]}");
        File.WriteAllText(Path.Combine(cacheDir, "_summary.json"), sb.ToString(), new UTF8Encoding(false));
    }

    // ─────────────────────────────────────────────────────────────
    // UI helpers
    // ─────────────────────────────────────────────────────────────
    private static int PromptAssetId(string title)
    {
        string s = EditorInputDialog.Show("NavMesh Exporter", title, "");
        if (string.IsNullOrEmpty(s)) return 0;
        int.TryParse(s.Trim(), out int r);
        return r;
    }

    private static bool PromptOpenSceneConfirm(List<SceneEntry> entries)
    {
        var active = EditorSceneManager.GetActiveScene();
        if (active.isDirty)
        {
            int ans = EditorUtility.DisplayDialogComplex(
                "场景有未保存修改",
                "当前活动场景 [" + active.name + "] 有未保存修改,继续将丢失这些修改。是否先保存?",
                "先保存再继续", "取消", "不保存直接继续");
            if (ans == 1) return false;
            if (ans == 0)
            {
                EditorSceneManager.SaveOpenScenes();
            }
        }
        string msg = "将依次打开 " + entries.Count + " 个场景并导出 NavMesh。\n第一条: "
            + entries[0].Name + " (AssetId=" + entries[0].AssetId + ")";
        return EditorUtility.DisplayDialog("确认批量导出", msg, "开始", "取消");
    }

    // ─────────────────────────────────────────────────────────────
    // JSON helpers
    // ─────────────────────────────────────────────────────────────
    private static void AppendKV(StringBuilder sb, string k, int v)
    {
        sb.Append('"').Append(k).Append("\":").Append(v);
    }
    private static void AppendKVF(StringBuilder sb, string k, float v)
    {
        sb.Append('"').Append(k).Append("\":");
        AppendFloat(sb, v);
    }
    private static void AppendKVStr(StringBuilder sb, string k, string v)
    {
        sb.Append('"').Append(k).Append("\":");
        AppendStr(sb, v);
    }
    private static void AppendVec3(StringBuilder sb, Vector3 v)
    {
        sb.Append('[');
        AppendFloat(sb, v.x); sb.Append(',');
        AppendFloat(sb, v.y); sb.Append(',');
        AppendFloat(sb, v.z);
        sb.Append(']');
    }
    private static void AppendFloat(StringBuilder sb, float v)
    {
        if (float.IsNaN(v) || float.IsInfinity(v)) { sb.Append("0"); return; }
        sb.Append(v.ToString("R", CultureInfo.InvariantCulture));
    }
    private static void AppendStr(StringBuilder sb, string s)
    {
        if (s == null) { sb.Append("null"); return; }
        sb.Append('"');
        foreach (char c in s)
        {
            switch (c)
            {
                case '"': sb.Append("\\\""); break;
                case '\\': sb.Append("\\\\"); break;
                case '\n': sb.Append("\\n"); break;
                case '\r': sb.Append("\\r"); break;
                case '\t': sb.Append("\\t"); break;
                default:
                    if (c < 0x20) sb.Append("\\u").Append(((int)c).ToString("X4"));
                    else sb.Append(c);
                    break;
            }
        }
        sb.Append('"');
    }
}

/// <summary>Minimal text input dialog (单行输入框)。</summary>
public class EditorInputDialog : EditorWindow
{
    private string _title, _message, _value, _result;
    private bool _ok;

    public static string Show(string title, string message, string defaultValue)
    {
        var w = CreateInstance<EditorInputDialog>();
        w.titleContent = new GUIContent(title);
        w._title = title;
        w._message = message;
        w._value = defaultValue ?? "";
        w.position = new Rect(Screen.currentResolution.width / 2 - 200,
                              Screen.currentResolution.height / 2 - 60, 400, 120);
        w.ShowModal();
        return w._ok ? w._result : null;
    }

    private void OnGUI()
    {
        EditorGUILayout.LabelField(_message, EditorStyles.wordWrappedLabel);
        _value = EditorGUILayout.TextField(_value);
        GUILayout.Space(6);
        using (new EditorGUILayout.HorizontalScope())
        {
            if (GUILayout.Button("OK")) { _ok = true; _result = _value; Close(); }
            if (GUILayout.Button("Cancel")) { _ok = false; Close(); }
        }
    }
}
#endif
