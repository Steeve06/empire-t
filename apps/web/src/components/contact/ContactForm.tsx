import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useApi } from "../../lib/api";
import { applyServerErrors, validators } from "../../lib/forms";
import { useLang, useT } from "../../lib/lang";
import { Field, inputClass } from "../forms/Field";
import { FormAlert } from "../forms/FormAlert";
import { Honeypot } from "../forms/Honeypot";
import { Button } from "../ui/Button";
import { CheckIcon } from "../ui/Icons";

const FIELDS = ["name", "contact", "message"] as const;

export function ContactForm() {
  const t = useT();
  const lang = useLang();
  const api = useApi();
  const [formError, setFormError] = useState<string | null>(null);

  const v = validators(t);
  const schema = z.object({
    name: v.name,
    contact: v.contact,
    message: z
      .string()
      .trim()
      .min(1, t("validation.required"))
      .min(10, t("validation.messageShort"))
      .max(2000, t("validation.tooLong", { max: 2000 })),
    website: v.honeypot,
  });
  type Values = z.infer<typeof schema>;
  const empty: Values = { name: "", contact: "", message: "", website: "" };

  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors },
  } = useForm<Values>({ resolver: zodResolver(schema), defaultValues: empty });

  const send = useMutation({
    mutationFn: (values: Values) => api.sendContact(lang, values),
    onError: (error) => {
      setFormError(applyServerErrors(error, FIELDS, setError, t));
    },
  });

  const onSubmit = handleSubmit(
    (values) => {
      setFormError(null);
      send.mutate(values);
    },
    () => {
      setFormError(t("validation.fixErrors"));
    },
  );

  if (send.isSuccess) {
    return (
      <div role="status" className="border border-gold bg-card p-6">
        <p className="flex size-11 items-center justify-center rounded-full bg-gold text-night">
          <CheckIcon />
        </p>
        <h3 className="mt-4 text-[30px]">{t("contact.success.title")}</h3>
        <p className="mt-2 text-muted">{t("contact.success.text")}</p>
        <Button
          variant="outline"
          className="mt-5"
          onClick={() => {
            reset(empty);
            send.reset();
          }}
        >
          {t("contact.success.another")}
        </Button>
      </div>
    );
  }

  return (
    <form noValidate onSubmit={(event) => void onSubmit(event)} className="relative grid gap-5">
      <h2 className="text-[clamp(30px,4vw,40px)]">{t("contact.formTitle")}</h2>
      <Field label={t("contact.name")} error={errors.name?.message}>
        <input type="text" autoComplete="name" className={inputClass} {...register("name")} />
      </Field>
      <Field label={t("contact.contact")} error={errors.contact?.message}>
        <input type="text" autoComplete="email" className={inputClass} {...register("contact")} />
      </Field>
      <Field label={t("contact.message")} error={errors.message?.message}>
        <textarea rows={5} className={inputClass} {...register("message")} />
      </Field>
      <Honeypot registration={register("website")} />
      <FormAlert>{formError}</FormAlert>
      <div>
        <Button type="submit" disabled={send.isPending} className="w-full sm:w-auto">
          {send.isPending ? t("contact.submitting") : t("contact.submit")}
        </Button>
      </div>
    </form>
  );
}
