import type { TFunction } from "i18next";
import type { FieldValues, Path, UseFormSetError } from "react-hook-form";
import { z } from "zod";

import { ApiError } from "@empire-t/api-client";

/** Cameroonian numbers (9 digits starting with 6 or 2, optional +237) or any +international number. */
const PHONE = /^(?:(?:\+|00)?237)?[26]\d{8}$|^\+\d{8,15}$/;
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export const compactPhone = (value: string) => value.replace(/[\s().-]/g, "");
export const isPhone = (value: string) => PHONE.test(compactPhone(value));
export const isEmail = (value: string) => EMAIL.test(value.trim());

/** Zod rules with messages in the page's language; the server validates again. */
export function validators(t: TFunction) {
  return {
    name: z
      .string()
      .trim()
      .min(1, t("validation.required"))
      .min(2, t("validation.nameShort"))
      .max(80, t("validation.tooLong", { max: 80 })),
    phone: z
      .string()
      .trim()
      .min(1, t("validation.required"))
      .refine(isPhone, t("validation.phone")),
    contact: z
      .string()
      .trim()
      .min(1, t("validation.required"))
      .max(254, t("validation.tooLong", { max: 254 }))
      .refine((value) => isEmail(value) || isPhone(value), t("validation.contact")),
    required: z.string().min(1, t("validation.required")),
    optionalText: (max: number) => z.string().trim().max(max, t("validation.tooLong", { max })),
    honeypot: z.string(),
  };
}

/**
 * Turns a failed submission into messages: DRF field errors go next to their
 * fields (when the form has them), everything else becomes the form-level message.
 */
export function applyServerErrors<T extends FieldValues>(
  error: unknown,
  fields: readonly Path<T>[],
  setError: UseFormSetError<T>,
  t: TFunction,
  /** Handlers for errors on inputs React Hook Form does not manage (the file list). */
  extra: Record<string, (message: string) => void> = {},
): string | null {
  if (!(error instanceof ApiError)) return t("status.errorServer");
  if (error.isNetworkError) return t("status.errorNetwork");
  if (error.isThrottled) return t("status.throttled");

  const unplaced: string[] = [];
  for (const [field, messages] of Object.entries(error.fieldErrors)) {
    // The first non-field error is already the ApiError's detail.
    const message = (field === "non_field_errors" ? messages.slice(1) : messages).join(" ");
    if (!message) continue;
    const handler = extra[field];
    if (handler) {
      handler(message);
    } else if ((fields as readonly string[]).includes(field)) {
      setError(field as Path<T>, { type: "server", message }, { shouldFocus: true });
    } else {
      unplaced.push(message);
    }
  }
  if (error.detail) unplaced.unshift(error.detail);
  if (unplaced.length) return unplaced.join(" ");
  return Object.keys(error.fieldErrors).length ? null : t("status.errorServer");
}
