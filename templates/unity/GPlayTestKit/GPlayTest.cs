using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.EventSystems;

namespace GPlay.TestKit
{
    /// <summary>
    /// The project writes ONE subclass (in any Editor assembly). It plays the game through the game's real input path
    /// (the same methods a tap / drag calls), and tells the context what happened.
    /// </summary>
    public abstract class GPlayTestDriver
    {
        /// <summary>Edit mode, before entering play mode: open (or build) the scene the run starts from.</summary>
        public virtual void Prepare(GPlayTestContext ctx) { }

        /// <summary>
        /// The run. Yield null = next frame, ctx.Wait(seconds), an AsyncOperation, or another IEnumerator.
        /// With -editmode the routine is pumped without play mode: the driver ticks the game itself.
        /// </summary>
        public abstract IEnumerator Run(GPlayTestContext ctx);
    }

    public sealed class GPlayWait
    {
        public float seconds;
        public bool realtime;
    }

    /// <summary>Arguments, screenshots, frame recording, UI checks and results of one run.</summary>
    public sealed class GPlayTestContext
    {
        [Serializable] class LevelResult { public string level; public bool won; public string note; }
        [Serializable] class VideoInfo { public string name; public string dir; public int fps; public int frames; public int width; public int height; }
        [Serializable]
        class Report
        {
            public bool ok;
            public int exitCode;
            public string outDir;
            public int width, height;
            public bool editMode, gpu;
            public List<LevelResult> levels = new List<LevelResult>();
            public List<string> shots = new List<string>();
            public List<VideoInfo> videos = new List<VideoInfo>();
            public int uiImages, uiStretched, uiTexts, uiOverflow, uiMissingGlyph, uiFallbackFont;
            public List<string> failures = new List<string>();
            public List<string> errors = new List<string>();
        }

        readonly string[] argv;
        readonly Report report = new Report();
        GPlayUiCheck.Result ui;
        VideoInfo video;
        float videoPrevCapture;
        int videoLastFrame = -1;

        public string OutDir { get; }
        public int Width { get; }
        public int Height { get; }
        public bool EditMode { get; }
        public IReadOnlyList<string> Levels { get; }
        public bool Recording => video != null;

        public GPlayTestContext()
        {
            argv = Environment.GetCommandLineArgs();
            OutDir = Path.GetFullPath(Arg("-out", Path.Combine(Path.GetTempPath(), "gplaytest"))).Replace('\\', '/');
            Directory.CreateDirectory(OutDir);
            var size = Arg("-size", "1080x1920").ToLowerInvariant().Split('x');
            Width = size.Length == 2 && int.TryParse(size[0], out var w) ? w : 1080;
            Height = size.Length == 2 && int.TryParse(size[1], out var h) ? h : 1920;
            EditMode = Flag("-editmode");
            Levels = ParseLevels(Arg("-levels", ""));
            report.outDir = OutDir; report.width = Width; report.height = Height;
            report.editMode = EditMode; report.gpu = GPlayCapture.HasGpu;
        }

        public bool Flag(string name) => Array.IndexOf(argv, name) >= 0;

        public string Arg(string name, string fallback)
        {
            int i = Array.IndexOf(argv, name);
            return i >= 0 && i + 1 < argv.Length ? argv[i + 1] : fallback;
        }

        /// <summary>"1-3,7,intro" → 1, 2, 3, 7, intro (the driver decides what a name means).</summary>
        public static List<string> ParseLevels(string spec)
        {
            var list = new List<string>();
            foreach (var raw in spec.Split(','))
            {
                var part = raw.Trim();
                if (part.Length == 0) continue;
                var ab = part.Split('-');
                if (ab.Length == 2 && int.TryParse(ab[0], out var a) && int.TryParse(ab[1], out var b) && b >= a)
                    for (int n = a; n <= b; n++) list.Add(n.ToString());
                else list.Add(part);
            }
            return list;
        }

        public GPlayWait Wait(float seconds, bool realtime = false) => new GPlayWait { seconds = seconds, realtime = realtime };

        public void Log(string msg) => Debug.Log("[GPlayTest] " + msg);

        /// <summary>Marks the run as failed (it still runs to the end).</summary>
        public void Fail(string msg)
        {
            report.failures.Add(msg);
            Debug.LogWarning("[GPlayTest] FAIL: " + msg);
        }

        /// <summary>False conditions fail the run with the message.</summary>
        public bool Expect(bool cond, string msg)
        {
            if (!cond) Fail(msg);
            return cond;
        }

        public void Result(string level, bool won, string note = "")
        {
            report.levels.Add(new LevelResult { level = level, won = won, note = note ?? "" });
            Debug.Log("[GPlayTest] " + level + ": " + (won ? "WIN" : "FAIL") + (string.IsNullOrEmpty(note) ? "" : " (" + note + ")"));
        }

        /// <summary>PNG of the camera + UI at the run size. Returns the full path (also when skipped for lack of a GPU).</summary>
        public string Shot(string name, bool withUi = true, Camera cam = null)
        {
            var path = OutDir + "/" + name + ".png";
            if (GPlayCapture.Shot(cam, path, Width, Height, withUi))
            {
                report.shots.Add(path);
                Debug.Log("[GPlayTest] shot " + path);
            }
            return path;
        }

        /// <summary>
        /// Starts a frame sequence in OutDir/video_name/. In play mode every frame is captured until EndVideo and game time
        /// advances exactly 1/fps per frame (Time.captureFramerate); in edit mode call Frame() after each tick.
        /// </summary>
        public void BeginVideo(string name, int fps = 30, int height = 960)
        {
            if (video != null) EndVideo();
            if (!GPlayCapture.HasGpu) { Debug.LogWarning("[GPlayTest] no GPU: video " + name + " skipped"); return; }
            int h = Mathf.Min(height, Height) / 2 * 2;
            int w = Mathf.RoundToInt(h * (float)Width / Height) / 2 * 2;
            video = new VideoInfo { name = name, dir = OutDir + "/video_" + name, fps = fps, width = w, height = h };
            if (Directory.Exists(video.dir)) Directory.Delete(video.dir, true);
            Directory.CreateDirectory(video.dir);
            videoPrevCapture = Time.captureFramerate;
            if (Application.isPlaying) Time.captureFramerate = fps;
            videoLastFrame = -1;
        }

        public void Frame(Camera cam = null)
        {
            if (video == null) return;
            if (Application.isPlaying)
            {
                if (Time.frameCount == videoLastFrame) return;
                videoLastFrame = Time.frameCount;
            }
            video.frames++;
            GPlayCapture.Shot(cam, video.dir + "/f_" + video.frames.ToString("D5") + ".jpg", video.width, video.height);
        }

        public void EndVideo()
        {
            if (video == null) return;
            if (Application.isPlaying) Time.captureFramerate = (int)videoPrevCapture;
            File.WriteAllText(video.dir + "/frames.json", JsonUtility.ToJson(video));
            report.videos.Add(video);
            Debug.Log("[GPlayTest] video " + video.name + ": " + video.frames + " frames @" + video.fps + " in " + video.dir);
            video = null;
        }

        /// <summary>Stretched images / text overflow / missing glyphs in the open scenes; totals go to the report.</summary>
        public GPlayUiCheck.Result UiCheck(string label)
        {
            var r = GPlayUiCheck.Run(label);
            ui.Add(r);
            return r;
        }

        /// <summary>Presses a UI object the way a pointer does (down, up, click handlers).</summary>
        public static bool Click(GameObject go)
        {
            if (go == null || !go.activeInHierarchy) return false;
            var ev = new PointerEventData(EventSystem.current) { button = PointerEventData.InputButton.Left };
            ExecuteEvents.ExecuteHierarchy(go, ev, ExecuteEvents.pointerDownHandler);
            ExecuteEvents.ExecuteHierarchy(go, ev, ExecuteEvents.pointerUpHandler);
            return ExecuteEvents.ExecuteHierarchy(go, ev, ExecuteEvents.pointerClickHandler) != null;
        }

        internal void OnLog(string condition, string stack, LogType type)
        {
            if (type != LogType.Error && type != LogType.Exception && type != LogType.Assert) return;
            if (EditorOnly(stack)) return; // editor housekeeping (search index, package manager...), not the game
            if (report.errors.Count < 30) report.errors.Add(type + ": " + condition);
            if (type == LogType.Exception) report.failures.Add("exception: " + condition);
        }

        /// <summary>True when every stack frame is System.* / UnityEditor.* (no game or UnityEngine frame).</summary>
        static bool EditorOnly(string stack)
        {
            if (string.IsNullOrEmpty(stack)) return false;
            bool any = false;
            foreach (var raw in stack.Split('\n'))
            {
                var line = raw.Trim();
                if (line.StartsWith("at ")) line = line.Substring(3);
                if (line.Length == 0) continue;
                any = true;
                if (!line.StartsWith("System.") && !line.StartsWith("UnityEditor.")) return false;
            }
            return any;
        }

        /// <summary>Writes report.json, logs the summary line, returns the exit code (0 ok, 1 failed).</summary>
        internal int Finish()
        {
            if (video != null) EndVideo();
            int won = 0;
            foreach (var l in report.levels) if (l.won) won++;
            report.uiImages = ui.images; report.uiStretched = ui.stretched; report.uiTexts = ui.texts;
            report.uiOverflow = ui.overflow; report.uiMissingGlyph = ui.missingGlyph; report.uiFallbackFont = ui.fallbackFont;
            bool bad = report.failures.Count > 0 || won < report.levels.Count
                       || (ui.Problems > 0 && !Flag("-allow-ui"))
                       || (report.errors.Count > 0 && !Flag("-allow-errors"));
            report.ok = !bad;
            report.exitCode = bad ? 1 : 0;
            File.WriteAllText(OutDir + "/report.json", JsonUtility.ToJson(report, true), new UTF8Encoding(false));
            Debug.Log("[GPlayTest] done: " + won + "/" + report.levels.Count + " won, failures " + report.failures.Count + ", errors "
                      + report.errors.Count + ", ui problems " + ui.Problems + ", shots " + report.shots.Count + ", videos "
                      + report.videos.Count + " -> " + OutDir + "/report.json");
            return report.exitCode;
        }
    }

    /// <summary>
    /// Entry points for -executeMethod:
    ///   GPlay.TestKit.GPlayTest.RunFromCommandLine  -levels 1-3 -out D:/tmp/playtest [-size 1080x1920] [-driver TypeName]
    ///                                               [-editmode] [-timeout 600] [-allow-ui] [-allow-errors] [project flags...]
    /// Do NOT pass -quit (the run exits Unity itself) and do NOT pass -nographics when screenshots are needed.
    /// </summary>
    [InitializeOnLoad]
    public static class GPlayTest
    {
        const string Key = "GPlay.TestKit.running";
        static GPlayTestContext ctx;
        static readonly Stack<IEnumerator> stack = new Stack<IEnumerator>();
        static double deadline;
        static float waitUntil;
        static double waitUntilReal;
        static AsyncOperation waitOp;
        static int lastFrame = -1;

        static GPlayTest()
        {
            // entering play mode reloads the domain: the flag survives, the hook does not
            if (SessionState.GetBool(Key, false)) EditorApplication.update += Pump;
        }

        public static void RunFromCommandLine()
        {
            var c = new GPlayTestContext();
            var driver = CreateDriver(c.Arg("-driver", ""));
            if (driver == null) { EditorApplication.Exit(3); return; }
            if (!GPlayCapture.HasGpu) Debug.LogWarning("[GPlayTest] running without a GPU: no screenshots / video");
            try { driver.Prepare(c); }
            catch (Exception e) { Debug.LogException(e); EditorApplication.Exit(3); return; }

            if (c.EditMode)
            {
                Application.logMessageReceived += c.OnLog;
                try { RunSync(driver.Run(c)); }
                catch (Exception e) { Debug.LogException(e); }
                EditorApplication.Exit(c.Finish());
                return;
            }
            SessionState.SetBool(Key, true);
            EditorApplication.update += Pump;
            EditorApplication.EnterPlaymode();
        }

        static GPlayTestDriver CreateDriver(string wanted)
        {
            var found = new List<Type>();
            foreach (var t in TypeCache.GetTypesDerivedFrom<GPlayTestDriver>())
                if (!t.IsAbstract && (wanted.Length == 0 || t.Name == wanted || t.FullName == wanted)) found.Add(t);
            if (found.Count != 1)
            {
                Debug.LogError("[GPlayTest] need exactly one GPlayTestDriver subclass" + (wanted.Length > 0 ? " named " + wanted : "")
                               + ", found " + found.Count + " (pick one with -driver <TypeName>)");
                return null;
            }
            return (GPlayTestDriver)Activator.CreateInstance(found[0]);
        }

        /// <summary>Edit mode: runs the routine to the end in one go; waits are skipped (the driver ticks the game).</summary>
        static void RunSync(IEnumerator root)
        {
            var st = new Stack<IEnumerator>();
            st.Push(root);
            int guard = 0;
            while (st.Count > 0)
            {
                if (++guard > 5000000) throw new Exception("GPlayTest: edit-mode routine did not finish");
                var top = st.Peek();
                if (!top.MoveNext()) { st.Pop(); continue; }
                if (top.Current is IEnumerator inner) st.Push(inner);
            }
        }

        static void Pump()
        {
            if (!SessionState.GetBool(Key, false)) { EditorApplication.update -= Pump; return; }
            double now = EditorApplication.timeSinceStartup;
            if (deadline <= 0)
            {
                float timeout = 600f;
                float.TryParse(new GPlayTestContext().Arg("-timeout", "600"), out timeout);
                deadline = now + timeout;
            }
            if (now > deadline)
            {
                if (ctx == null) ctx = new GPlayTestContext();
                ctx.Fail("timeout: the run did not finish (play mode not entered, or the driver is stuck)");
                Exit();
                return;
            }
            if (!EditorApplication.isPlaying) return; // still entering play mode
            if (ctx == null)
            {
                ctx = new GPlayTestContext();
                Application.logMessageReceived += ctx.OnLog;
                var driver = CreateDriver(ctx.Arg("-driver", ""));
                if (driver == null) { ctx.Fail("no driver"); Exit(); return; }
                stack.Clear();
                stack.Push(driver.Run(ctx));
            }
            if (Time.frameCount == lastFrame) return; // one step per game frame
            lastFrame = Time.frameCount;

            bool waiting = (waitOp != null && !waitOp.isDone) || Time.time < waitUntil || now < waitUntilReal;
            if (!waiting)
            {
                waitOp = null;
                if (!Step()) return; // finished
            }
            if (ctx.Recording) ctx.Frame();
        }

        /// <summary>Advances the routine up to its next yield. False when the run ended.</summary>
        static bool Step()
        {
            while (true)
            {
                var top = stack.Peek();
                bool moved;
                try { moved = top.MoveNext(); }
                catch (Exception e)
                {
                    Debug.LogException(e);
                    ctx.Fail("driver threw: " + e.Message);
                    Exit();
                    return false;
                }
                if (!moved)
                {
                    stack.Pop();
                    if (stack.Count == 0) { Exit(); return false; }
                    continue; // resume the parent in the same frame
                }
                switch (top.Current)
                {
                    case IEnumerator inner: stack.Push(inner); continue;
                    case GPlayWait w:
                        if (w.realtime) waitUntilReal = EditorApplication.timeSinceStartup + w.seconds;
                        else waitUntil = Time.time + w.seconds;
                        return true;
                    case AsyncOperation op: waitOp = op; return true;
                    default: return true; // null and anything else: next frame
                }
            }
        }

        static void Exit()
        {
            SessionState.SetBool(Key, false);
            EditorApplication.update -= Pump;
            int code = ctx != null ? ctx.Finish() : 1;
            EditorApplication.Exit(code);
        }
    }
}
