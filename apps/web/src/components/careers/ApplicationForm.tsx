import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useId, useState, type ChangeEvent } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { JobOpening } from "@empire-t/api-client";

import { useApi } from "../../lib/api";
import { applyServerErrors, validators } from "../../lib/forms";
import { useLang, useT } from "../../lib/lang";
import { ACCEPT_ATTRIBUTE, checkUploads, formatBytes } from "../../lib/uploads";
import { Field, inputClass } from "../forms/Field";
import { FormAlert } from "../forms/FormAlert";
import { Honeypot } from "../forms/Honeypot";
import { Button } from "../ui/Button";
import { CheckIcon, CloseIcon, UploadIcon } from "../ui/Icons";

const FIELDS = ["opening", "full_name", "contact", "message"] as const;

export function ApplicationForm({ openings }: { openings: JobOpening[] }) {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const filesId = useId();
  const [files, setFiles] = useState<File[]>([]);
  const [filesError, setFilesError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const v = validators(t);
  const schema = z.object({
    opening: v.required,
    full_name: v.name.max(100, t("validation.tooLong", { max: 100 })),
    contact: v.contact,
    message: v.optionalText(1000),
    website: v.honeypot,
  });
  type Values = z.infer<typeof schema>;
  const empty: Values = {
    opening: openings.length === 1 ? (openings[0]?.slug ?? "") : "",
    full_name: "",
    contact: "",
    message: "",
    website: "",
  };

  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema), defaultValues: empty });

  const application = useMutation({
    mutationFn: (values: Values) => api.apply(lang, { ...values, files }),
    onSuccess: () => {
      setSent(true);
    },
    onError: (error) => {
      setFormError(applyServerErrors(error, FIELDS, setError, t, { files: setFilesError }));
    },
  });

  function onFilesChosen(event: ChangeEvent<HTMLInputElement>) {
    const chosen = Array.from(event.currentTarget.files ?? []);
    event.currentTarget.value = ""; // allows choosing the same file again after removing it
    const next = [
      ...files,
      ...chosen.filter((file) => !files.some((f) => f.name === file.name && f.size === file.size)),
    ];
    setFiles(next);
    setFilesError(checkUploads(next, t));
  }

  function removeFile(file: File) {
    const next = files.filter((item) => item !== file);
    setFiles(next);
    setFilesError(next.length ? checkUploads(next, t) : null);
  }

  const onSubmit = handleSubmit(
    (values) => {
      const problem = checkUploads(files, t);
      setFilesError(problem);
      setFormError(problem ? t("validation.fixErrors") : null);
      if (!problem) application.mutate(values);
    },
    () => {
      setFilesError(checkUploads(files, t));
      setFormError(t("validation.fixErrors"));
    },
  );

  if (sent) {
    return (
      <div role="status" className="border border-gold bg-card p-6">
        <p className="flex size-11 items-center justify-center rounded-full bg-gold text-night">
          <CheckIcon />
        </p>
        <h3 className="mt-4 text-[30px]">{t("careers.success.title")}</h3>
        <p className="mt-2 text-muted">{t("careers.success.text")}</p>
        <Button
          variant="outline"
          className="mt-5"
          onClick={() => {
            reset(empty);
            setFiles([]);
            setSent(false);
          }}
        >
          {t("careers.success.another")}
        </Button>
      </div>
    );
  }

  const total = files.reduce((sum, file) => sum + file.size, 0);

  return (
    <form noValidate onSubmit={(event) => void onSubmit(event)} className="relative grid gap-5">
      <h3 className="text-[30px]">{t("careers.formTitle")}</h3>
      <Field label={t("careers.position")} error={errors.opening?.message}>
        <select className={inputClass} {...register("opening")}>
          <option value="">{t("careers.choosePosition")}</option>
          {openings.map((opening) => (
            <option key={opening.slug} value={opening.slug}>
              {opening.title}
            </option>
          ))}
        </select>
      </Field>
      <Field label={t("careers.fullName")} error={errors.full_name?.message}>
        <input type="text" autoComplete="name" className={inputClass} {...register("full_name")} />
      </Field>
      <Field label={t("careers.contact")} error={errors.contact?.message}>
        <input
          type="text"
          autoComplete="email"
          placeholder={t("careers.contactPlaceholder")}
          className={inputClass}
          {...register("contact")}
        />
      </Field>
      <Field label={t("careers.message")} error={errors.message?.message}>
        <textarea rows={3} className={inputClass} {...register("message")} />
      </Field>

      <fieldset
        className="grid gap-2"
        aria-describedby={`${filesId}-hint${filesError ? ` ${filesId}-error` : ""}`}
      >
        <legend className="mb-1.5 text-xs font-semibold tracking-[0.1em] text-muted uppercase">
          {t("careers.files")}
        </legend>
        <label
          htmlFor={filesId}
          className="flex min-h-14 cursor-pointer items-center justify-center gap-2 border border-dashed border-gold-ink bg-card px-4 text-sm font-semibold text-gold-ink focus-within:outline-2 focus-within:outline-gold hover:bg-page"
        >
          <UploadIcon />
          {t("careers.files")}
          <input
            id={filesId}
            type="file"
            multiple
            accept={ACCEPT_ATTRIBUTE}
            onChange={onFilesChosen}
            className="sr-only"
          />
        </label>
        <p id={`${filesId}-hint`} className="text-[13px] text-muted">
          {t("careers.filesHint")}
        </p>
        {files.length ? (
          <ul className="divide-y divide-line border border-line bg-card text-sm">
            {files.map((file) => (
              <li
                key={`${file.name}-${file.size}`}
                className="flex items-center gap-3 py-1 pr-1 pl-3"
              >
                <span className="min-w-0 flex-1 truncate">{file.name}</span>
                <span className="shrink-0 text-muted">{formatBytes(file.size, lang)}</span>
                <button
                  type="button"
                  onClick={() => {
                    removeFile(file);
                  }}
                  aria-label={t("careers.removeFile", { name: file.name })}
                  className="flex size-11 shrink-0 items-center justify-center text-muted hover:text-danger"
                >
                  <CloseIcon width={18} height={18} />
                </button>
              </li>
            ))}
            <li className="py-2 pr-3 text-right text-xs text-muted">{formatBytes(total, lang)}</li>
          </ul>
        ) : null}
        {filesError ? (
          <p id={`${filesId}-error`} role="alert" className="text-[13px] font-medium text-danger">
            {filesError}
          </p>
        ) : null}
      </fieldset>

      <Honeypot registration={register("website")} />
      <FormAlert>{formError}</FormAlert>
      <div>
        <Button type="submit" disabled={application.isPending} className="w-full sm:w-auto">
          {application.isPending ? t("careers.submitting") : t("careers.submit")}
        </Button>
      </div>
    </form>
  );
}
