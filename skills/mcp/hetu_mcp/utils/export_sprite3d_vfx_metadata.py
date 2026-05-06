from __future__ import annotations

"""Export Sprite3D/Role and VFX metadata into resource files and resource_index.

Workflow:
1. Optionally refresh mcp/hetu_mcp/resource/resource_index.json by running
   export_resource_list.py.
2. Read all Sprite3D, Role, and VFX rows from resource_index.json.
3. Download their AssetBundle .ab files into mcp/temp by default. This path
   is intentionally beside hetu_mcp instead of using an absolute temp drive.
4. Generate temporary Unity Editor code, run it in batchmode, set the
   AssetBundle decrypt key, and parse the cached .ab files.
5. Delta-update slim sprite_3d.json and vfx.json outputs from parsed rows.
6. Write the parsed fields back to matching rows in resource_index.json.

Unity parsing rules:
- Sprite3D/Role: first MeshPartSettings found in the prefab provides
  animations, center, size, bodyType, and direction. The root prefab transform
  provides rootRotation and rootScale.
- VFX with ParticleSystem: root particle systems use main.duration; nested
  particle systems use startDelayMax + startLifetimeMax; vfxTime is the max.
- VFX without ParticleSystem: all Animation components contribute their first
  clip length; vfxTime is the max first-clip length; isLoop is true when any
  first clip is Loop or PingPong.
"""

import argparse
import concurrent.futures
import json
import os
import shutil
import ssl
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
from urllib.request import HTTPSHandler, build_opener


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MCP_ROOT = PACKAGE_ROOT.parent
DEFAULT_RESOURCE_DIR = PACKAGE_ROOT / "resource"
DEFAULT_CACHE_DIR = MCP_ROOT / "temp"
RESOURCE_INDEX_FILENAME = "resource_index.json"
SPRITE3D_FILENAME = "sprite_3d.json"
VFX_FILENAME = "vfx.json"
SPRITE3D_PARSED_FILENAME = "sprite_3d_parsed.json"
VFX_PARSED_FILENAME = "vfx_parsed.json"
DECRYPT_KEY = "0123456789abcdef"
SPRITE3D_RESOURCE_TYPES = ("Sprite3D", "Role")


SPRITE3D_FIELDS = [
    "rootRotation",
    "rootScale",
    "animations",
    "center",
    "size",
    "bodyType",
    "direction",
]
VFX_FIELDS = ["isLoop", "vfxTime"]


UNITY_EXPORTER_TEMPLATE = r'''
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using VeryFS.Creation.Common;

public static class __CLASS_NAME__
{
    private class BundleJob
    {
        public int EntryId;
        public int ResourceId;
        public string ResourceName;
        public string File;
        public string Url;
        public long Size;
        public string Md5;
    }

    public static void RunFromCommandLine()
    {
        try
        {
            Dictionary<string, string> args = ParseArgs(Environment.GetCommandLineArgs());
            string cacheDir = GetArg(args, "--hetu-cache-dir", "");
            string resourceDir = GetArg(args, "--hetu-resource-dir", "");
            string decryptKey = GetArg(args, "--hetu-decrypt-key", "0123456789abcdef");

            if (string.IsNullOrEmpty(cacheDir) || string.IsNullOrEmpty(resourceDir))
            {
                throw new Exception("Missing --hetu-cache-dir or --hetu-resource-dir.");
            }

            AssetBundle.SetAssetBundleDecryptKey(decryptKey);
            Directory.CreateDirectory(resourceDir);

            string spriteManifest = Path.Combine(cacheDir, "Sprite3D_manifest.tsv");
            string vfxManifest = Path.Combine(cacheDir, "VFX_manifest.tsv");
            JArray spriteRows = ParseSprite3D(ReadManifest(spriteManifest));
            JArray vfxRows = ParseVFX(ReadManifest(vfxManifest));

            File.WriteAllText(
                Path.Combine(cacheDir, "sprite_3d_parsed.json"),
                spriteRows.ToString(Formatting.Indented),
                new System.Text.UTF8Encoding(false));
            File.WriteAllText(
                Path.Combine(cacheDir, "vfx_parsed.json"),
                vfxRows.ToString(Formatting.Indented),
                new System.Text.UTF8Encoding(false));

            JObject summary = new JObject();
            summary["sprite3d_role"] = spriteRows.Count;
            summary["vfx"] = vfxRows.Count;
            summary["resourceDir"] = resourceDir;
            File.WriteAllText(
                Path.Combine(cacheDir, "Sprite3D_Role_VFX_parse_summary.json"),
                summary.ToString(Formatting.Indented),
                new System.Text.UTF8Encoding(false));
            Debug.Log("[Hetu] Sprite3D/Role/VFX metadata export completed: " + summary.ToString(Formatting.None));
        }
        catch (Exception ex)
        {
            Debug.LogError("[Hetu] Sprite3D/Role/VFX metadata export failed: " + ex);
            EditorApplication.Exit(1);
        }
    }

    private static Dictionary<string, string> ParseArgs(string[] args)
    {
        Dictionary<string, string> result = new Dictionary<string, string>();
        for (int i = 0; i < args.Length; i++)
        {
            if (!args[i].StartsWith("--")) continue;
            string value = "true";
            if (i + 1 < args.Length && !args[i + 1].StartsWith("--"))
            {
                value = args[i + 1];
                i++;
            }
            result[args[i]] = value;
        }
        return result;
    }

    private static string GetArg(Dictionary<string, string> args, string name, string fallback)
    {
        string value;
        return args.TryGetValue(name, out value) ? value : fallback;
    }

    private static List<BundleJob> ReadManifest(string path)
    {
        List<BundleJob> jobs = new List<BundleJob>();
        if (!File.Exists(path)) throw new FileNotFoundException("Manifest not found.", path);

        foreach (string line in File.ReadLines(path))
        {
            if (line.StartsWith("entry_id\t") || string.IsNullOrWhiteSpace(line)) continue;
            string[] cols = line.Split('\t');
            if (cols.Length < 7) continue;
            BundleJob job = new BundleJob();
            int.TryParse(cols[0], out job.EntryId);
            int.TryParse(cols[1], out job.ResourceId);
            job.ResourceName = cols[2];
            job.File = cols[3];
            job.Url = cols[4];
            long.TryParse(cols[5], out job.Size);
            job.Md5 = cols[6];
            jobs.Add(job);
        }
        return jobs;
    }

    private static JArray ParseSprite3D(List<BundleJob> jobs)
    {
        JArray rows = new JArray();
        foreach (BundleJob job in jobs)
        {
            JObject row = new JObject();
            row["resource_id"] = job.ResourceId;
            row["rootRotation"] = JValue.CreateNull();
            row["rootScale"] = JValue.CreateNull();
            row["animations"] = new JArray();
            row["center"] = JValue.CreateNull();
            row["size"] = JValue.CreateNull();
            row["bodyType"] = JValue.CreateNull();
            row["direction"] = JValue.CreateNull();

            AssetBundle ab = null;
            try
            {
                ab = AssetBundle.LoadFromFile(job.File);
                if (ab == null)
                {
                    rows.Add(row);
                    continue;
                }

                MeshPartSettings selected = null;
                GameObject selectedRoot = null;
                string[] assetNames = ab.GetAllAssetNames();
                for (int i = 0; i < assetNames.Length && selected == null; i++)
                {
                    GameObject root = ab.LoadAsset<GameObject>(assetNames[i]);
                    if (root == null) continue;
                    MeshPartSettings[] settings = root.GetComponentsInChildren<MeshPartSettings>(true);
                    if (settings.Length == 0) continue;
                    selected = settings[0];
                    selectedRoot = root;
                }

                if (selected != null)
                {
                    row["rootRotation"] = Vec3(selectedRoot.transform.localEulerAngles);
                    row["rootScale"] = Vec3(selectedRoot.transform.localScale);
                    row["animations"] = Animations(selected.animations);
                    row["center"] = Vec3(selected.center);
                    row["size"] = Vec3(selected.size);
                    row["bodyType"] = selected.bodyType.ToString();
                    row["direction"] = selected.direction.ToString();
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning("[Hetu] Sprite3D/Role parse failed for " + job.ResourceId + ": " + ex.Message);
            }
            finally
            {
                if (ab != null) ab.Unload(true);
            }
            rows.Add(row);
        }
        return rows;
    }

    private static JArray ParseVFX(List<BundleJob> jobs)
    {
        JArray rows = new JArray();
        foreach (BundleJob job in jobs)
        {
            JObject row = new JObject();
            row["resource_id"] = job.ResourceId;
            row["resource_name"] = job.ResourceName;
            row["isLoop"] = false;
            row["vfxTime"] = JValue.CreateNull();

            AssetBundle ab = null;
            try
            {
                ab = AssetBundle.LoadFromFile(job.File);
                if (ab == null)
                {
                    rows.Add(row);
                    continue;
                }

                List<ParticleSystem> particleSystems = new List<ParticleSystem>();
                List<GameObject> roots = new List<GameObject>();
                string[] assetNames = ab.GetAllAssetNames();
                for (int i = 0; i < assetNames.Length; i++)
                {
                    GameObject root = ab.LoadAsset<GameObject>(assetNames[i]);
                    if (root == null) continue;
                    roots.Add(root);
                    particleSystems.AddRange(root.GetComponentsInChildren<ParticleSystem>(true));
                }

                if (particleSystems.Count > 0)
                {
                    FillParticleVFX(row, roots, particleSystems);
                }
                else
                {
                    FillAnimationVFX(row, roots);
                }
            }
            catch (Exception ex)
            {
                Debug.LogWarning("[Hetu] VFX parse failed for " + job.ResourceId + ": " + ex.Message);
            }
            finally
            {
                if (ab != null) ab.Unload(true);
            }
            rows.Add(row);
        }
        return rows;
    }

    private static void FillParticleVFX(JObject row, List<GameObject> roots, List<ParticleSystem> systems)
    {
        Dictionary<ParticleSystem, string> paths = new Dictionary<ParticleSystem, string>();
        HashSet<string> particlePaths = new HashSet<string>();

        for (int i = 0; i < systems.Count; i++)
        {
            ParticleSystem ps = systems[i];
            GameObject root = FindRoot(roots, ps.transform);
            string path = PathOf(ps.transform, root == null ? null : root.transform);
            paths[ps] = path;
            particlePaths.Add(path);
        }

        bool isLoop = false;
        bool hasValue = false;
        float maxTime = 0f;
        for (int i = 0; i < systems.Count; i++)
        {
            ParticleSystem ps = systems[i];
            ParticleSystem.MainModule main = ps.main;
            if (main.loop) isLoop = true;

            string path = paths[ps];
            bool isSubParticle = HasParticleAncestor(path, particlePaths);
            float candidate = isSubParticle
                ? MaxCurve(main.startDelay) + MaxCurve(main.startLifetime)
                : main.duration;

            if (!hasValue || candidate > maxTime) maxTime = candidate;
            hasValue = true;
        }

        row["isLoop"] = isLoop;
        row["vfxTime"] = hasValue ? new JValue(CleanNumber(maxTime)) : JValue.CreateNull();
    }

    private static void FillAnimationVFX(JObject row, List<GameObject> roots)
    {
        bool anyClip = false;
        bool anyLoop = false;
        float maxLength = 0f;

        for (int r = 0; r < roots.Count; r++)
        {
            Animation[] animations = roots[r].GetComponentsInChildren<Animation>(true);
            for (int i = 0; i < animations.Length; i++)
            {
                AnimationClip clip;
                AnimationState state;
                if (!TryGetFirstClip(animations[i], out clip, out state)) continue;

                anyClip = true;
                if (clip.length > maxLength) maxLength = clip.length;
                WrapMode stateWrap = state != null ? state.wrapMode : WrapMode.Default;
                WrapMode clipWrap = clip.wrapMode;
                if (IsLoopWrap(stateWrap) || (stateWrap == WrapMode.Default && IsLoopWrap(clipWrap)))
                {
                    anyLoop = true;
                }
            }
        }

        row["isLoop"] = anyLoop;
        row["vfxTime"] = anyClip ? new JValue(CleanNumber(maxLength)) : JValue.CreateNull();
    }

    private static bool TryGetFirstClip(Animation animation, out AnimationClip clip, out AnimationState state)
    {
        clip = null;
        state = null;
        if (animation == null) return false;

        clip = animation.clip;
        if (clip != null)
        {
            try { state = animation[clip.name]; }
            catch { state = null; }
            return true;
        }

        foreach (AnimationState candidate in animation)
        {
            if (candidate == null || candidate.clip == null) continue;
            state = candidate;
            clip = candidate.clip;
            return true;
        }
        return false;
    }

    private static bool IsLoopWrap(WrapMode wrapMode)
    {
        return wrapMode == WrapMode.Loop || wrapMode == WrapMode.PingPong;
    }

    private static GameObject FindRoot(List<GameObject> roots, Transform transform)
    {
        Transform current = transform;
        while (current != null)
        {
            for (int i = 0; i < roots.Count; i++)
            {
                if (roots[i] != null && current == roots[i].transform) return roots[i];
            }
            current = current.parent;
        }
        return roots.Count > 0 ? roots[0] : null;
    }

    private static bool HasParticleAncestor(string path, HashSet<string> particlePaths)
    {
        if (string.IsNullOrEmpty(path)) return false;
        string[] parts = path.Split('/');
        for (int i = 1; i < parts.Length; i++)
        {
            string ancestor = string.Join("/", parts, 0, i);
            if (particlePaths.Contains(ancestor)) return true;
        }
        return false;
    }

    private static float MaxCurve(ParticleSystem.MinMaxCurve curve)
    {
        switch (curve.mode)
        {
            case ParticleSystemCurveMode.Constant:
                return curve.constant;
            case ParticleSystemCurveMode.TwoConstants:
                return curve.constantMax;
            case ParticleSystemCurveMode.Curve:
                return MaxCurveValue(curve.curve) * curve.curveMultiplier;
            case ParticleSystemCurveMode.TwoCurves:
                return Mathf.Max(MaxCurveValue(curve.curveMin), MaxCurveValue(curve.curveMax)) * curve.curveMultiplier;
            default:
                return curve.constantMax;
        }
    }

    private static float MaxCurveValue(AnimationCurve curve)
    {
        if (curve == null || curve.length == 0) return 0f;
        float max = float.MinValue;
        Keyframe[] keys = curve.keys;
        for (int i = 0; i < keys.Length; i++)
        {
            if (keys[i].value > max) max = keys[i].value;
        }
        return max == float.MinValue ? 0f : max;
    }

    private static string PathOf(Transform transform, Transform root)
    {
        List<string> names = new List<string>();
        Transform current = transform;
        while (current != null)
        {
            names.Add(current.name);
            if (current == root) break;
            current = current.parent;
        }
        names.Reverse();
        return string.Join("/", names.ToArray());
    }

    private static JArray Vec3(Vector3 value)
    {
        return new JArray(CleanNumber(value.x), CleanNumber(value.y), CleanNumber(value.z));
    }

    private static JArray Animations(List<AnimationData> animations)
    {
        JArray rows = new JArray();
        if (animations == null) return rows;
        for (int i = 0; i < animations.Count; i++)
        {
            AnimationData item = animations[i];
            if (item == null) continue;
            JObject row = new JObject();
            row["stateName"] = item.stateName;
            row["loop"] = item.loop;
            row["duration"] = new JValue(CleanNumber(item.duration));
            rows.Add(row);
        }
        return rows;
    }

    private static object CleanNumber(float value)
    {
        if (float.IsNaN(value) || float.IsInfinity(value)) return null;
        double rounded = Math.Round(value, 6);
        if (Math.Abs(rounded - Math.Round(rounded)) < 0.0000001)
        {
            return (int)Math.Round(rounded);
        }
        return rounded;
    }
}
'''


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Update resource_index.json, download Sprite3D/Role/VFX AssetBundles, "
            "parse them in Unity, export sprite_3d.json/vfx.json, and write parsed "
            "fields back to resource_index.json."
        )
    )
    parser.add_argument(
        "--resource-dir",
        default=str(DEFAULT_RESOURCE_DIR),
        help="Directory containing resource_index.json. Defaults to mcp/hetu_mcp/resource.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help="AssetBundle cache directory. Defaults to mcp/temp, beside hetu_mcp.",
    )
    parser.add_argument(
        "--unity-project",
        default=os.environ.get("UNITY_PROJECT", ""),
        help="Unity project path. Required unless --skip-unity is used.",
    )
    parser.add_argument(
        "--unity-exe",
        default=os.environ.get("UNITY_EXE", ""),
        help="Unity Editor executable path. If omitted, the script tries to find Unity.exe on PATH.",
    )
    parser.add_argument(
        "--decrypt-key",
        default=DECRYPT_KEY,
        help="AssetBundle decrypt key.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=12,
        help="Parallel AssetBundle download workers.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="Download timeout in seconds.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Skip TLS verification when downloading resource list or AssetBundles.",
    )
    parser.add_argument(
        "--skip-resource-update",
        action="store_true",
        help="Do not call export_resource_list.py before processing.",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Reuse existing files in the cache directory and only regenerate manifests.",
    )
    parser.add_argument(
        "--skip-unity",
        action="store_true",
        help="Skip Unity parsing and reuse existing sprite_3d.json/vfx.json.",
    )
    parser.add_argument(
        "--skip-index-writeback",
        action="store_true",
        help="Do not write parsed Sprite3D/Role/VFX fields back to resource_index.json.",
    )
    parser.add_argument(
        "--keep-unity-script",
        action="store_true",
        help="Keep the temporary generated Unity Editor script in Assets/Editor.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_resource_update(args: argparse.Namespace, resource_dir: Path) -> None:
    if args.skip_resource_update:
        return

    exporter = Path(__file__).with_name("export_resource_list.py")
    cmd = [
        sys.executable,
        str(exporter),
        "--output",
        str(resource_dir),
    ]
    if args.insecure:
        cmd.append("--insecure")
    print("Updating resource_index.json...")
    subprocess.run(cmd, check=True)


def resource_type(record: dict[str, Any]) -> str:
    return str(record.get("resource_type") or record.get("entry_type") or "")


def pick_assetbundle_url(record: dict[str, Any]) -> str:
    primary = str(record.get("primary_url") or "")
    if primary.lower().endswith(".ab"):
        return primary
    for storage in record.get("storages") or []:
        if not isinstance(storage, dict):
            continue
        url = str(storage.get("url") or "")
        if url.lower().endswith(".ab"):
            return url
    return primary


def build_jobs(records: list[dict[str, Any]], kind: str, cache_dir: Path) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    prefix = kind.lower()
    for record in records:
        if resource_type(record) != kind:
            continue
        url = pick_assetbundle_url(record)
        filename = Path(urlparse(url).path).name or f"{record.get('resource_id')}.ab"
        cache_name = f"{prefix}_{record.get('resource_id')}_{filename}"
        jobs.append(
            {
                "entry_id": record.get("entry_id"),
                "resource_id": record.get("resource_id"),
                "resource_name": record.get("resource_name") or "",
                "url": url,
                "size": int(record.get("primary_size") or 0),
                "md5": record.get("primary_md5") or "",
                "file": str(cache_dir / cache_name),
            }
        )
    return jobs


def build_jobs_for_types(records: list[dict[str, Any]], kinds: tuple[str, ...], cache_dir: Path) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for kind in kinds:
        jobs.extend(build_jobs(records, kind, cache_dir))
    return jobs


def write_manifest(cache_dir: Path, kind: str, jobs: list[dict[str, Any]]) -> Path:
    path = cache_dir / f"{kind}_manifest.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write("entry_id\tresource_id\tresource_name\tfile\turl\tsize\tmd5\n")
        for job in jobs:
            values = [
                job["entry_id"],
                job["resource_id"],
                job["resource_name"],
                job["file"],
                job["url"],
                job["size"],
                job["md5"],
            ]
            handle.write(
                "\t".join(str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ") for value in values)
                + "\n"
            )
    return path


def make_opener(insecure: bool):
    if insecure:
        context = ssl._create_unverified_context()
    else:
        context = ssl.create_default_context()
    opener = build_opener(HTTPSHandler(context=context))
    opener.addheaders = [("User-Agent", "HetuAIGC-Sprite3D-Role-VFX-export/1.0")]
    return opener


def download_one(job: dict[str, Any], opener, timeout: int) -> tuple[str, int, str | None]:
    path = Path(str(job["file"]))
    expected = int(job.get("size") or 0)
    if path.exists() and (not expected or path.stat().st_size == expected):
        return ("cached", int(job["resource_id"]), None)

    part = path.with_suffix(path.suffix + ".part")
    last_error = None
    for attempt in range(3):
        try:
            with opener.open(str(job["url"]), timeout=timeout) as response, part.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    handle.write(chunk)
            if expected and part.stat().st_size != expected:
                raise IOError(f"size mismatch: got {part.stat().st_size}, expected {expected}")
            part.replace(path)
            return ("downloaded", int(job["resource_id"]), None)
        except Exception as exc:  # noqa: BLE001
            last_error = repr(exc)
            if part.exists():
                part.unlink()
            time.sleep(1 + attempt)
    return ("failed", int(job["resource_id"]), last_error)


def download_bundles(
    kind: str,
    jobs: list[dict[str, Any]],
    cache_dir: Path,
    workers: int,
    timeout: int,
    insecure: bool,
    skip_download: bool,
    label: str | None = None,
) -> None:
    display_name = label or kind
    write_manifest(cache_dir, kind, jobs)
    if skip_download:
        print(f"{display_name}: manifest written, download skipped ({len(jobs)} jobs).")
        return

    opener = make_opener(insecure)
    counts = {"cached": 0, "downloaded": 0, "failed": 0}
    failures: list[dict[str, Any]] = []
    print(f"{display_name}: downloading {len(jobs)} AssetBundles to {cache_dir}...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_job = {pool.submit(download_one, job, opener, timeout): job for job in jobs}
        for done, future in enumerate(concurrent.futures.as_completed(future_to_job), start=1):
            job = future_to_job[future]
            try:
                status, _, error = future.result()
            except Exception as exc:  # noqa: BLE001
                status, error = "failed", repr(exc)
            counts[status] += 1
            if status == "failed":
                failures.append({**job, "error": error})
            if done % 50 == 0 or done == len(jobs):
                print(
                    f"{display_name}: {done}/{len(jobs)} "
                    f"cached={counts['cached']} downloaded={counts['downloaded']} failed={counts['failed']}"
                )

    failures_path = cache_dir / f"{kind}_download_failures.json"
    failures_path.write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        raise RuntimeError(f"{display_name}: {len(failures)} AssetBundle downloads failed. See {failures_path}")


def resolve_unity_exe(value: str) -> str:
    if value:
        return value
    found = shutil.which("Unity")
    if found:
        return found
    found = shutil.which("Unity.exe")
    if found:
        return found
    raise RuntimeError("Unity executable not found. Pass --unity-exe or set UNITY_EXE.")


def write_unity_exporter(unity_project: Path) -> tuple[Path, str]:
    class_name = f"HetuResourceMetadataExporter_{os.getpid()}"
    editor_dir = unity_project / "Assets" / "Editor"
    editor_dir.mkdir(parents=True, exist_ok=True)
    script_path = editor_dir / f"{class_name}.cs"
    script_path.write_text(UNITY_EXPORTER_TEMPLATE.replace("__CLASS_NAME__", class_name), encoding="utf-8")
    return script_path, class_name


def run_unity_parser(args: argparse.Namespace, resource_dir: Path, cache_dir: Path) -> None:
    if args.skip_unity:
        return
    if not args.unity_project:
        raise RuntimeError("Unity project path is required. Pass --unity-project or set UNITY_PROJECT.")

    unity_project = Path(args.unity_project).resolve()
    unity_exe = resolve_unity_exe(args.unity_exe)
    script_path, class_name = write_unity_exporter(unity_project)
    log_path = cache_dir / "unity_sprite3d_role_vfx_export.log"
    cmd = [
        unity_exe,
        "-batchmode",
        "-quit",
        "-projectPath",
        str(unity_project),
        "-executeMethod",
        f"{class_name}.RunFromCommandLine",
        "-logFile",
        str(log_path),
        "--hetu-cache-dir",
        str(cache_dir),
        "--hetu-resource-dir",
        str(resource_dir),
        "--hetu-decrypt-key",
        args.decrypt_key,
    ]
    print(f"Running Unity parser. Log: {log_path}")
    try:
        subprocess.run(cmd, check=True)
    finally:
        if not args.keep_unity_script:
            script_path.unlink(missing_ok=True)
            script_path.with_suffix(".cs.meta").unlink(missing_ok=True)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def scalar_to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def dumps_compact_vectors(value: Any, level: int = 0) -> str:
    indent = "  " * level
    child_indent = "  " * (level + 1)
    if isinstance(value, dict):
        if not value:
            return "{}"
        parts = [
            f"{child_indent}{scalar_to_json(key)}: {dumps_compact_vectors(item, level + 1)}"
            for key, item in value.items()
        ]
        return "{\n" + ",\n".join(parts) + "\n" + indent + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        if len(value) in (3, 4) and all(is_number(item) for item in value):
            return "[" + ",".join(scalar_to_json(item) for item in value) + "]"
        parts = [f"{child_indent}{dumps_compact_vectors(item, level + 1)}" for item in value]
        return "[\n" + ",\n".join(parts) + "\n" + indent + "]"
    return scalar_to_json(value)


def coerce_resource_id(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def load_resource_rows(path: Path, *, required: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Parsed metadata file not found: {path}")
        return []

    payload = load_json(path)
    if isinstance(payload, dict):
        payload = payload.get("resources", [])
    if not isinstance(payload, list):
        return []
    return [row for row in payload if isinstance(row, dict)]


def normalize_sprite_row(row: dict[str, Any]) -> dict[str, Any] | None:
    resource_id = coerce_resource_id(row.get("resource_id"))
    if resource_id is None:
        return None
    return {
        "resource_id": resource_id,
        "rootRotation": row.get("rootRotation"),
        "rootScale": row.get("rootScale"),
        "animations": row.get("animations"),
        "center": row.get("center"),
        "size": row.get("size"),
        "bodyType": row.get("bodyType"),
        "direction": row.get("direction"),
    }


def normalize_vfx_row(row: dict[str, Any]) -> dict[str, Any] | None:
    resource_id = coerce_resource_id(row.get("resource_id"))
    if resource_id is None:
        return None
    return {
        "resource_id": resource_id,
        "resource_name": row.get("resource_name"),
        "isLoop": row.get("isLoop"),
        "vfxTime": row.get("vfxTime"),
    }


def normalize_rows(
    rows: list[dict[str, Any]],
    normalizer: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        normalized_row = normalizer(row)
        if normalized_row is not None:
            normalized.append(normalized_row)
    return normalized


def merge_delta_rows(
    existing_rows: list[dict[str, Any]],
    parsed_rows: list[dict[str, Any]],
    normalizer: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> tuple[list[dict[str, Any]], int, int]:
    rows_by_id: dict[int, dict[str, Any]] = {}
    order: list[int] = []

    for row in normalize_rows(existing_rows, normalizer):
        resource_id = int(row["resource_id"])
        if resource_id not in rows_by_id:
            order.append(resource_id)
        rows_by_id[resource_id] = row

    updated = 0
    appended = 0
    for row in normalize_rows(parsed_rows, normalizer):
        resource_id = int(row["resource_id"])
        if resource_id in rows_by_id:
            updated += 1
        else:
            order.append(resource_id)
            appended += 1
        rows_by_id[resource_id] = row

    return [rows_by_id[resource_id] for resource_id in order], updated, appended


def normalize_outputs(
    resource_dir: Path,
    cache_dir: Path,
    *,
    use_parsed_outputs: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sprite_path = resource_dir / SPRITE3D_FILENAME
    vfx_path = resource_dir / VFX_FILENAME

    existing_sprite_rows = load_resource_rows(sprite_path)
    existing_vfx_rows = load_resource_rows(vfx_path)

    if use_parsed_outputs:
        sprite_source_path = cache_dir / SPRITE3D_PARSED_FILENAME
        vfx_source_path = cache_dir / VFX_PARSED_FILENAME
        parsed_sprite_rows = load_resource_rows(sprite_source_path, required=True)
        parsed_vfx_rows = load_resource_rows(vfx_source_path, required=True)
        normalized_sprite, sprite_updated, sprite_appended = merge_delta_rows(
            existing_sprite_rows,
            parsed_sprite_rows,
            normalize_sprite_row,
        )
        normalized_vfx, vfx_updated, vfx_appended = merge_delta_rows(
            existing_vfx_rows,
            parsed_vfx_rows,
            normalize_vfx_row,
        )
        print(
            "sprite_3d.json delta update: "
            f"updated={sprite_updated}, appended={sprite_appended}, total={len(normalized_sprite)}"
        )
        print(
            "vfx.json delta update: "
            f"updated={vfx_updated}, appended={vfx_appended}, total={len(normalized_vfx)}"
        )
    else:
        normalized_sprite = normalize_rows(existing_sprite_rows, normalize_sprite_row)
        normalized_vfx = normalize_rows(existing_vfx_rows, normalize_vfx_row)
        print(
            "sprite_3d.json normalized from existing rows: "
            f"total={len(normalized_sprite)}"
        )
        print(f"vfx.json normalized from existing rows: total={len(normalized_vfx)}")

    sprite_path.write_text(dumps_compact_vectors(normalized_sprite) + "\n", encoding="utf-8")
    vfx_path.write_text(
        json.dumps(normalized_vfx, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return normalized_sprite, normalized_vfx


def writeback_resource_index(
    resource_dir: Path,
    sprite_rows: list[dict[str, Any]],
    vfx_rows: list[dict[str, Any]],
) -> None:
    index_path = resource_dir / RESOURCE_INDEX_FILENAME
    records = load_json(index_path)
    sprite_by_id = {int(row["resource_id"]): row for row in sprite_rows if row.get("resource_id") is not None}
    vfx_by_id = {int(row["resource_id"]): row for row in vfx_rows if row.get("resource_id") is not None}

    sprite_updated = 0
    vfx_updated = 0
    for record in records:
        resource_id = record.get("resource_id")
        if resource_id is None:
            continue
        rid = int(resource_id)
        sprite = sprite_by_id.get(rid)
        if sprite is not None:
            for field in SPRITE3D_FIELDS:
                record[field] = sprite.get(field)
            sprite_updated += 1

        vfx = vfx_by_id.get(rid)
        if vfx is not None:
            for field in VFX_FIELDS:
                record[field] = vfx.get(field)
            vfx_updated += 1

    index_path.write_text(dumps_compact_vectors(records) + "\n", encoding="utf-8")
    print(f"resource_index.json writeback: Sprite3D/Role={sprite_updated}, VFX={vfx_updated}")


def validate_json(path: Path) -> None:
    load_json(path)


def main() -> int:
    args = parse_args()
    resource_dir = Path(args.resource_dir).resolve()
    cache_dir = Path(args.cache_dir).resolve()
    resource_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    run_resource_update(args, resource_dir)

    index_path = resource_dir / RESOURCE_INDEX_FILENAME
    records = load_json(index_path)
    sprite_jobs = build_jobs_for_types(records, SPRITE3D_RESOURCE_TYPES, cache_dir)
    sprite_type_counts = {
        kind: sum(1 for record in records if resource_type(record) == kind)
        for kind in SPRITE3D_RESOURCE_TYPES
    }
    vfx_jobs = build_jobs(records, "VFX", cache_dir)
    print(
        "Found "
        + ", ".join(f"{kind}={sprite_type_counts[kind]}" for kind in SPRITE3D_RESOURCE_TYPES)
        + f", VFX={len(vfx_jobs)} in {index_path}"
    )

    download_bundles(
        "Sprite3D",
        sprite_jobs,
        cache_dir,
        args.workers,
        args.timeout,
        args.insecure,
        args.skip_download,
        label="Sprite3D/Role",
    )
    download_bundles(
        "VFX",
        vfx_jobs,
        cache_dir,
        args.workers,
        args.timeout,
        args.insecure,
        args.skip_download,
    )

    run_unity_parser(args, resource_dir, cache_dir)
    sprite_rows, vfx_rows = normalize_outputs(
        resource_dir,
        cache_dir,
        use_parsed_outputs=not args.skip_unity,
    )

    if not args.skip_index_writeback:
        writeback_resource_index(resource_dir, sprite_rows, vfx_rows)

    for filename in [RESOURCE_INDEX_FILENAME, SPRITE3D_FILENAME, VFX_FILENAME]:
        validate_json(resource_dir / filename)

    print(f"Done. Cache: {cache_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
