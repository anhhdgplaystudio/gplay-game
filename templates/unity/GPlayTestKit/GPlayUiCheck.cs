using System.Collections.Generic;
using System.Text.RegularExpressions;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace GPlay.TestKit
{
    /// <summary>
    /// Cheap UI checks for the open scenes:
    /// stretched images (rect aspect differs from the sprite aspect, or uneven scale),
    /// text overflowing its box, characters missing from the font, characters drawn with a fallback font.
    /// Each problem is logged as a warning with the object path.
    /// </summary>
    public static class GPlayUiCheck
    {
        public struct Result
        {
            public int images, stretched, texts, overflow, missingGlyph, fallbackFont;
            public int Problems => stretched + overflow + missingGlyph;
            public void Add(Result o)
            {
                images += o.images; stretched += o.stretched; texts += o.texts;
                overflow += o.overflow; missingGlyph += o.missingGlyph; fallbackFont += o.fallbackFont;
            }
        }

        /// <summary>Aspect tolerance (2 %).</summary>
        public static float Tolerance = 0.02f;
        /// <summary>Also require the native pixel size (not only the aspect). Off: any even scale is fine.</summary>
        public static bool RequireNativeSize = false;
        /// <summary>Object names skipped by the stretch check (full-screen tints made from a white sprite...).</summary>
        public static readonly List<string> IgnoreNames = new List<string> { "Backdrop", "Overlay", "Dim", "Blocker", "Fade" };

        static readonly Regex Tags = new Regex("<[^>]+>");

        public static Result Run(string label)
        {
            var r = new Result();
            for (int s = 0; s < SceneManager.sceneCount; s++)
            {
                var scene = SceneManager.GetSceneAt(s);
                if (!scene.isLoaded) continue;
                foreach (var root in scene.GetRootGameObjects()) Check(root, ref r);
            }
            // objects moved to DontDestroyOnLoad in play mode
            if (Application.isPlaying)
                foreach (var c in Object.FindObjectsByType<Canvas>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                    if (c.isRootCanvas && c.gameObject.scene.name == "DontDestroyOnLoad") Check(c.gameObject, ref r);
            Debug.Log("[GPlayUiCheck] " + label + ": images " + r.images + ", stretched " + r.stretched + "; texts " + r.texts
                      + ", overflow " + r.overflow + ", missing glyph " + r.missingGlyph + ", fallback font " + r.fallbackFont);
            return r;
        }

        static void Check(GameObject root, ref Result r)
        {
            foreach (var img in root.GetComponentsInChildren<Image>(true))
            {
                if (img.sprite == null || img.type != Image.Type.Simple || img.preserveAspect) continue;
                if (img.GetComponent<AspectRatioFitter>() != null) continue; // cover-fit background
                if (IgnoreNames.Contains(img.name)) continue;
                r.images++;
                var why = ImageProblem(img);
                if (why == null) continue;
                r.stretched++;
                Debug.LogWarning("[GPlayUiCheck] stretched: " + PathOf(img.transform) + " (" + img.sprite.name + "): " + why);
            }
            foreach (var t in root.GetComponentsInChildren<TMP_Text>(true))
            {
                if (string.IsNullOrEmpty(t.text) || t.font == null) continue;
                r.texts++;
                string plain = t.richText ? Tags.Replace(t.text, "") : t.text;
                if (!t.font.HasCharacters(plain, out uint[] missing, true, true) && missing != null && missing.Length > 0)
                {
                    r.missingGlyph++;
                    Debug.LogWarning("[GPlayUiCheck] missing glyph: " + PathOf(t.transform) + " font " + t.font.name + ": "
                                     + Chars(missing) + " in \"" + Short(plain) + "\"");
                }
                if (!t.gameObject.activeInHierarchy) continue; // layout of inactive text is not reliable
                t.ForceMeshUpdate(true);
                var info = t.textInfo;
                bool fallback = false;
                for (int i = 0; i < info.characterCount && !fallback; i++)
                {
                    var ci = info.characterInfo[i];
                    if (ci.isVisible && ci.fontAsset != null && ci.fontAsset != t.font) fallback = true;
                }
                if (fallback)
                {
                    r.fallbackFont++;
                    Debug.LogWarning("[GPlayUiCheck] fallback font (mixed typefaces): " + PathOf(t.transform) + " \"" + Short(plain) + "\"");
                }
                var rect = t.rectTransform.rect;
                bool wide = rect.width > 1f && t.textBounds.size.x > rect.width + 2f;
                if (t.isTextOverflowing || wide)
                {
                    r.overflow++;
                    Debug.LogWarning("[GPlayUiCheck] text overflow: " + PathOf(t.transform) + " box " + rect.size + " text "
                                     + (Vector2)t.textBounds.size + " \"" + Short(plain) + "\"");
                }
            }
        }

        static string ImageProblem(Image img)
        {
            var native = img.sprite.rect.size;
            var size = img.rectTransform.rect.size;
            if (size.x <= 0f || size.y <= 0f) return null; // collapsed / driven by a layout not built yet
            float aspect = (size.x / size.y) / (native.x / native.y);
            if (Mathf.Abs(aspect - 1f) > Tolerance)
                return "aspect off by " + Mathf.RoundToInt((aspect - 1f) * 100f) + "% (rect " + size + ", sprite " + native + ")";
            if (RequireNativeSize)
            {
                var unit = native * (100f / img.sprite.pixelsPerUnit);
                if (Mathf.Abs(size.x / unit.x - 1f) > Tolerance) return "rect " + size + " is not the native size " + unit;
            }
            for (Transform p = img.rectTransform; p != null && p.GetComponent<Canvas>() == null; p = p.parent)
            {
                var sc = p.localScale;
                if (Mathf.Abs(sc.y) < 1e-4f) continue; // collapsed while animating
                if (Mathf.Abs(Mathf.Abs(sc.x) / Mathf.Abs(sc.y) - 1f) > Tolerance) return "uneven scale " + sc + " on " + p.name;
            }
            return null;
        }

        static string Chars(uint[] codes)
        {
            var sb = new System.Text.StringBuilder();
            for (int i = 0; i < codes.Length && i < 12; i++)
                sb.Append(codes[i] < 0x10000 ? ((char)codes[i]).ToString() : "?").Append("(U+").Append(codes[i].ToString("X4")).Append(") ");
            return sb.ToString();
        }

        static string Short(string s) => s.Length <= 40 ? s : s.Substring(0, 40) + "...";

        public static string PathOf(Transform t)
        {
            var s = t.name;
            for (var p = t.parent; p != null; p = p.parent) s = p.name + "/" + s;
            return s;
        }
    }
}
