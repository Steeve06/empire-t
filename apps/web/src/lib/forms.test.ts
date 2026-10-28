import { describe, expect, it, vi } from "vitest";

import { ApiError } from "@empire-t/api-client";

import { createI18n } from "../i18n";
import { applyServerErrors, isEmail, isPhone } from "./forms";
import { checkUploads, formatBytes } from "./uploads";

const t = createI18n("en").getFixedT("en");

describe("contact details", () => {
  it.each([
    "653147512",
    "6 53 14 75 12",
    "+237 653 147 512",
    "00237653147512",
    "222 23 45 67",
    "+33 6 12 34 56 78",
  ])("accepts the phone number %s", (value) => {
    expect(isPhone(value)).toBe(true);
  });

  it.each(["12345", "553147512", "+1", "abc"])("rejects the phone number %s", (value) => {
    expect(isPhone(value)).toBe(false);
  });

  it("recognises email addresses", () => {
    expect(isEmail("awa@mail.cm")).toBe(true);
    expect(isEmail("awa@mail")).toBe(false);
  });
});

describe("applyServerErrors", () => {
  it("puts field errors on their fields and returns the rest", () => {
    const setError = vi.fn();
    const files = vi.fn();
    const error = new ApiError(400, {
      phone: ["Invalid number."],
      files: ["“x.exe”: unsupported format."],
      non_field_errors: ["Slot taken."],
    });
    const message = applyServerErrors(error, ["phone"] as const, setError, t, { files });
    expect(setError).toHaveBeenCalledWith(
      "phone",
      { type: "server", message: "Invalid number." },
      { shouldFocus: true },
    );
    expect(files).toHaveBeenCalledWith("“x.exe”: unsupported format.");
    expect(message).toBe("Slot taken.");
  });

  it("explains network failures and throttling in plain words", () => {
    const setError = vi.fn();
    expect(applyServerErrors(new ApiError(0, null), [], setError, t)).toMatch(/connection/);
    expect(applyServerErrors(new ApiError(429, { detail: "x" }), [], setError, t)).toMatch(
      /Too many attempts/,
    );
    expect(applyServerErrors(new Error("boom"), [], setError, t)).toMatch(/briefly unavailable/);
  });
});

describe("checkUploads", () => {
  const file = (name: string, size: number) => {
    const blob = new File(["x"], name);
    Object.defineProperty(blob, "size", { value: size });
    return blob;
  };
  const MB = 1024 * 1024;

  it("mirrors the API's limits", () => {
    expect(checkUploads([], t)).toBe("Add at least one document.");
    expect(checkUploads([file("cv.pdf", MB)], t)).toBeNull();
    expect(checkUploads([file("CV.PDF", MB), file("work.MOV", 14 * MB)], t)).toBeNull();
    expect(checkUploads([file("run.exe", 10)], t)).toMatch(/run.exe: unsupported format/);
    expect(checkUploads([file("big.mp4", 16 * MB)], t)).toBe("big.mp4 is larger than 15 MB.");
    expect(
      checkUploads(
        Array.from({ length: 9 }, (_, i) => file(`${i}.jpg`, 10)),
        t,
      ),
    ).toBe("Up to 8 files.");
    expect(
      checkUploads([file("a.mp4", 14 * MB), file("b.mp4", 14 * MB), file("c.mp4", 14 * MB)], t),
    ).toBe("The total is larger than 40 MB.");
  });

  it("formats sizes for each language", () => {
    expect(formatBytes(2.5 * MB, "fr").replace(/\s/g, " ")).toBe("2,5 Mo");
    expect(formatBytes(2.5 * MB, "en").replace(/\s/g, " ")).toBe("2.5 MB");
    expect(formatBytes(300 * 1024, "en").replace(/\s/g, " ")).toBe("300 KB");
  });
});
