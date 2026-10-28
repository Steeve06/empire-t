import { describe, expect, it, vi } from "vitest";

import { ApiError, createApiClient, toFormData } from "./index";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("ApiError", () => {
  it("separates the detail message from field errors", () => {
    const error = new ApiError(400, {
      detail: "Nope",
      phone: ["Numéro invalide."],
      name: "Trop court",
    });
    expect(error.detail).toBe("Nope");
    expect(error.fieldErrors).toEqual({ phone: ["Numéro invalide."], name: ["Trop court"] });
    expect(error.message).toBe("Nope");
  });

  it("falls back to non_field_errors for the detail", () => {
    const error = new ApiError(400, { non_field_errors: ["Créneau pris."] });
    expect(error.detail).toBe("Créneau pris.");
  });

  it("flags network and throttling failures", () => {
    expect(new ApiError(0, null).isNetworkError).toBe(true);
    expect(new ApiError(429, { detail: "Slow down" }).isThrottled).toBe(true);
  });
});

describe("createApiClient", () => {
  it("sends the language and returns typed data", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>((input) => {
      expect(input instanceof Request ? input.url : String(input)).toBe(
        "https://api.test/api/v1/supplements/?lang=en",
      );
      return Promise.resolve(jsonResponse(200, [{ id: 1, name: "Hot towel", price: 500 }]));
    });
    const api = createApiClient({
      baseUrl: "https://api.test",
      fetch,
    });
    await expect(api.supplements("en")).resolves.toEqual([
      { id: 1, name: "Hot towel", price: 500 },
    ]);
  });

  it("throws ApiError with the server's field errors", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(() =>
      Promise.resolve(jsonResponse(400, { phone: ["Numéro invalide."] })),
    );
    const api = createApiClient({
      baseUrl: "https://api.test",
      fetch,
    });
    const call = api.sendContact("fr", { name: "Ana", contact: "x", message: "Bonjour à vous" });
    await expect(call).rejects.toMatchObject({
      status: 400,
      fieldErrors: { phone: ["Numéro invalide."] },
    });
  });

  it("turns a network failure into ApiError status 0", async () => {
    const fetch = vi.fn<typeof globalThis.fetch>(() =>
      Promise.reject(new TypeError("Failed to fetch")),
    );
    const api = createApiClient({
      baseUrl: "https://api.test",
      fetch,
    });
    const error: unknown = await api.site("fr").catch((caught: unknown) => caught);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).isNetworkError).toBe(true);
  });
});

describe("toFormData", () => {
  it("encodes every file under the same `files` key", () => {
    const form = toFormData({
      opening: "barber-titulaire",
      full_name: "Paul Mbarga",
      contact: "653147512",
      files: [new File(["a"], "cv.pdf"), new File(["b"], "cni.jpg")],
    });
    expect(form.getAll("files").map((file) => (file as File).name)).toEqual(["cv.pdf", "cni.jpg"]);
    expect(form.get("website")).toBe("");
    expect(form.has("message")).toBe(false);
  });
});
