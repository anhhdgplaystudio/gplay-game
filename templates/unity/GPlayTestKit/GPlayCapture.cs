using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Rendering;

namespace GPlay.TestKit
{
    /// <summary>
    /// Renders a camera (plus the screen-space UI) to an image of an exact size. Works in edit mode and play mode,
    /// in batchmode with a GPU (not with -nographics).
    /// </summary>
    public static class GPlayCapture
    {
        public static bool HasGpu => SystemInfo.graphicsDeviceType != GraphicsDeviceType.Null;

        struct Swapped { public Canvas canvas; public RenderMode mode; public Camera cam; public float dist; }

        /// <summary>Camera used when the caller passes none: main camera, any camera, or a temporary UI-only one.</summary>
        static Camera Pick(Camera cam, out Camera temp)
        {
            temp = null;
            if (cam != null) return cam;
            cam = Camera.main;
            if (cam == null) cam = Object.FindFirstObjectByType<Camera>();
            if (cam != null) return cam;
            var go = new GameObject("GPlayCaptureCamera") { hideFlags = HideFlags.HideAndDontSave };
            temp = go.AddComponent<Camera>();
            temp.clearFlags = CameraClearFlags.SolidColor;
            temp.backgroundColor = Color.black;
            temp.orthographic = true;
            temp.cullingMask = 1 << 5; // UI layer
            return temp;
        }

        /// <summary>Caller destroys the texture. Overlay canvases are laid out at w x h for the shot, then restored.</summary>
        public static Texture2D Render(Camera cam, int w, int h, bool withUi = true)
        {
            cam = Pick(cam, out var temp);
            var rt = RenderTexture.GetTemporary(w, h, 24, RenderTextureFormat.ARGB32);
            var prevTarget = cam.targetTexture;
            var prevActive = RenderTexture.active;
            var swapped = new List<Swapped>();
            cam.targetTexture = rt; // canvas scalers read the camera pixel size
            if (withUi)
            {
                foreach (var c in Object.FindObjectsByType<Canvas>(FindObjectsSortMode.None))
                {
                    if (!c.isRootCanvas || !c.isActiveAndEnabled || c.renderMode != RenderMode.ScreenSpaceOverlay) continue;
                    swapped.Add(new Swapped { canvas = c, mode = c.renderMode, cam = c.worldCamera, dist = c.planeDistance });
                    c.renderMode = RenderMode.ScreenSpaceCamera;
                    c.worldCamera = cam;
                    c.planeDistance = cam.nearClipPlane + 0.05f;
                }
                Canvas.ForceUpdateCanvases();
            }
            var req = new RenderPipeline.StandardRequest { destination = rt };
            if (RenderPipeline.SupportsRenderRequest(cam, req)) RenderPipeline.SubmitRenderRequest(cam, req);
            else cam.Render();
            RenderTexture.active = rt;
            var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            RenderTexture.active = prevActive;
            cam.targetTexture = prevTarget;
            foreach (var s in swapped)
            {
                s.canvas.renderMode = s.mode;
                s.canvas.worldCamera = s.cam;
                s.canvas.planeDistance = s.dist;
            }
            if (swapped.Count > 0) Canvas.ForceUpdateCanvases();
            RenderTexture.ReleaseTemporary(rt);
            if (temp != null) Object.DestroyImmediate(temp.gameObject);
            return tex;
        }

        /// <summary>Saves .png or .jpg by extension. False (with a warning) when there is no GPU.</summary>
        public static bool Shot(Camera cam, string path, int w, int h, bool withUi = true, int jpgQuality = 82)
        {
            if (!HasGpu)
            {
                Debug.LogWarning("[GPlayTest] no GPU (-nographics): skipped " + path);
                return false;
            }
            var tex = Render(cam, w, h, withUi);
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
            bool jpg = path.EndsWith(".jpg", System.StringComparison.OrdinalIgnoreCase);
            File.WriteAllBytes(path, jpg ? tex.EncodeToJPG(jpgQuality) : tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            return true;
        }
    }
}
