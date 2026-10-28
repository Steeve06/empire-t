import type { Lang } from "@empire-t/api-client";
import type { TFunction } from "i18next";

/** Mirrors the API's limits (apps/careers/uploads.py) so people learn about problems before uploading. */
export const UPLOAD_LIMITS = {
  maxFiles: 8,
  maxFileBytes: 15 * 1024 * 1024,
  maxTotalBytes: 40 * 1024 * 1024,
  extensions: [
    "pdf",
    "doc",
    "docx",
    "jpg",
    "jpeg",
    "png",
    "webp",
    "heic",
    "heif",
    "mp4",
    "m4v",
    "mov",
  ],
} as const;

export const ACCEPT_ATTRIBUTE = UPLOAD_LIMITS.extensions.map((ext) => `.${ext}`).join(",");

const extension = (name: string) => name.split(".").pop()?.toLowerCase() ?? "";

/** The first problem with a set of files, in the page's language, or null. */
export function checkUploads(files: readonly File[], t: TFunction): string | null {
  if (!files.length) return t("validation.filesRequired");
  if (files.length > UPLOAD_LIMITS.maxFiles) return t("validation.filesTooMany");
  for (const file of files) {
    if (!(UPLOAD_LIMITS.extensions as readonly string[]).includes(extension(file.name))) {
      return t("validation.fileType", { name: file.name });
    }
    if (file.size > UPLOAD_LIMITS.maxFileBytes)
      return t("validation.fileTooBig", { name: file.name });
  }
  const total = files.reduce((sum, file) => sum + file.size, 0);
  return total > UPLOAD_LIMITS.maxTotalBytes ? t("validation.filesTotal") : null;
}

/** "320 Ko" / "2,4 Mo" in French, "320 KB" / "2.4 MB" in English. */
export function formatBytes(bytes: number, lang: Lang): string {
  const [kilo, mega] = lang === "fr" ? ["Ko", "Mo"] : ["KB", "MB"];
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))}\u00a0${kilo}`;
  const value = new Intl.NumberFormat(lang, { maximumFractionDigits: 1 }).format(
    bytes / (1024 * 1024),
  );
  return `${value}\u00a0${mega}`;
}
