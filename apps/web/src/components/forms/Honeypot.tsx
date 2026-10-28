import type { UseFormRegisterReturn } from "react-hook-form";

/**
 * Anti-spam trap matching the API's `website` field: invisible to people and
 * skipped by keyboard and screen readers, but filled in by naive bots.
 */
export function Honeypot({ registration }: { registration: UseFormRegisterReturn }) {
  return (
    <div aria-hidden="true" className="absolute -left-[9999px] h-px w-px overflow-hidden">
      <label>
        Website
        <input type="text" tabIndex={-1} autoComplete="off" {...registration} />
      </label>
    </div>
  );
}
