/**
 * Typed client for the Empire T API.
 *
 * Types come from `schema.d.ts`, generated from the Django OpenAPI schema
 * (`make api-client`), so a backend contract change breaks the frontend build
 * instead of breaking production.
 */
import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

type Schemas = components["schemas"];

export type Lang = "fr" | "en";
export type SiteSettings = Schemas["SiteSettings"];
export type ServiceCategory = Schemas["ServiceCategory"];
export type Service = Schemas["Service"];
export type ServiceInCategory = Schemas["ServiceInCategory"];
export type Supplement = Schemas["Supplement"];
export type GalleryImage = Schemas["GalleryImage"];
export type GalleryCategory = Schemas["GalleryCategoryEnum"];
export type Testimonial = Schemas["Testimonial"];
export type TeamMember = Schemas["TeamMember"];
export type JobOpening = Schemas["JobOpening"];
export type ResponsiveImage = Schemas["ResponsiveImageSchema"];
export type BookingInput = Schemas["BookingCreateRequest"];
export type BookingCreated = Schemas["BookingCreated"];
export type AvailableSlots = Schemas["AvailableSlots"];
export type ContactInput = Schemas["ContactMessageCreateRequest"];

export interface ApplicationInput {
  opening: string;
  full_name: string;
  contact: string;
  message?: string;
  files: readonly File[];
  website?: string;
}

/** Field name to messages, as returned by DRF validation errors. */
export type FieldErrors = Record<string, string[]>;

/**
 * Any failed call. `status` is 0 when the network failed before a response
 * (offline, DNS, timeout): the UI shows a "check your connection" message then.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly fieldErrors: FieldErrors;
  readonly detail: string | undefined;

  constructor(status: number, body: unknown) {
    const { detail, fieldErrors } = parseErrorBody(body);
    super(detail ?? `API request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.fieldErrors = fieldErrors;
  }

  get isNetworkError(): boolean {
    return this.status === 0;
  }

  get isThrottled(): boolean {
    return this.status === 429;
  }
}

function parseErrorBody(body: unknown): { detail: string | undefined; fieldErrors: FieldErrors } {
  const fieldErrors: FieldErrors = {};
  let detail: string | undefined;
  if (body && typeof body === "object" && !Array.isArray(body)) {
    for (const [key, value] of Object.entries(body as Record<string, unknown>)) {
      if (key === "detail" && typeof value === "string") {
        detail = value;
      } else if (Array.isArray(value)) {
        fieldErrors[key] = value.filter((item): item is string => typeof item === "string");
      } else if (typeof value === "string") {
        fieldErrors[key] = [value];
      }
    }
  }
  if (!detail && fieldErrors.non_field_errors?.[0]) {
    detail = fieldErrors.non_field_errors[0];
  }
  return { detail, fieldErrors };
}

async function unwrap<T>(
  call: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  let result: { data?: T; error?: unknown; response: Response };
  try {
    result = await call;
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiError(0, { detail: cause instanceof Error ? cause.message : String(cause) });
  }
  const { data, error, response } = result;
  if (error !== undefined || data === undefined) {
    throw new ApiError(response.status, error);
  }
  return data;
}

export interface ApiClientOptions {
  /** Origin of the API, without `/api/v1` (empty string for same-origin requests). */
  baseUrl: string;
  /** Injected in tests and during pre-rendering. */
  fetch?: typeof globalThis.fetch;
}

export function createApiClient({ baseUrl, fetch }: ApiClientOptions) {
  const client = createClient<paths>({ baseUrl, ...(fetch ? { fetch } : {}) });

  return {
    site: (lang: Lang) => unwrap(client.GET("/api/v1/site/", { params: { query: { lang } } })),

    categories: (lang: Lang) =>
      unwrap(client.GET("/api/v1/categories/", { params: { query: { lang } } })),

    supplements: (lang: Lang) =>
      unwrap(client.GET("/api/v1/supplements/", { params: { query: { lang } } })),

    gallery: (
      lang: Lang,
      query: { category?: GalleryCategory; featured?: boolean; page?: number } = {},
    ) => unwrap(client.GET("/api/v1/gallery/", { params: { query: { lang, ...query } } })),

    testimonials: (lang: Lang) =>
      unwrap(client.GET("/api/v1/testimonials/", { params: { query: { lang } } })),

    team: (lang: Lang) => unwrap(client.GET("/api/v1/team/", { params: { query: { lang } } })),

    openings: (lang: Lang) =>
      unwrap(client.GET("/api/v1/careers/openings/", { params: { query: { lang } } })),

    slots: (date: string, service?: string, signal?: AbortSignal) =>
      unwrap(
        client.GET("/api/v1/bookings/slots/", {
          params: { query: { date, ...(service ? { service } : {}) } },
          ...(signal ? { signal } : {}),
        }),
      ),

    createBooking: (lang: Lang, body: BookingInput) =>
      unwrap(client.POST("/api/v1/bookings/", { params: { query: { lang } }, body })),

    sendContact: (lang: Lang, body: ContactInput) =>
      unwrap(client.POST("/api/v1/contact/", { params: { query: { lang } }, body })),

    apply: (lang: Lang, input: ApplicationInput) =>
      unwrap(
        client.POST("/api/v1/careers/applications/", {
          params: { query: { lang } },
          // The generated type describes files as strings; the real payload is multipart.
          body: input as unknown as Schemas["JobApplicationCreateRequest"],
          bodySerializer: () => toFormData(input),
        }),
      ),
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;

export function toFormData(input: ApplicationInput): FormData {
  const form = new FormData();
  form.append("opening", input.opening);
  form.append("full_name", input.full_name);
  form.append("contact", input.contact);
  if (input.message) form.append("message", input.message);
  form.append("website", input.website ?? "");
  for (const file of input.files) form.append("files", file, file.name);
  return form;
}
