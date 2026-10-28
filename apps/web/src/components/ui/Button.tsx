import type { ComponentProps } from "react";
import { Link } from "react-router";

import { buttonClass, type ButtonVariant } from "./buttonStyles";

type ButtonProps = ComponentProps<"button"> & { variant?: ButtonVariant };

export function Button({ variant = "gold", className, type = "button", ...props }: ButtonProps) {
  return <button type={type} className={buttonClass(variant, className)} {...props} />;
}

type ButtonLinkProps = ComponentProps<typeof Link> & { variant?: ButtonVariant };

export function ButtonLink({ variant = "gold", className, ...props }: ButtonLinkProps) {
  return <Link className={buttonClass(variant, className)} {...props} />;
}
