import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const defaults: IconProps = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
  focusable: false,
};

export const MenuIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </svg>
);

export const CloseIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
);

export const ChevronDownIcon = (props: IconProps) => (
  <svg {...defaults} width={14} height={14} {...props}>
    <path d="M6 9l6 6 6-6" />
  </svg>
);

export const ChevronLeftIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M15 18l-6-6 6-6" />
  </svg>
);

export const ChevronRightIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M9 18l6-6-6-6" />
  </svg>
);

/** Generic chat bubble with a handset (not the WhatsApp trademark). */
export const ChatIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M20.5 11.6a8.4 8.4 0 0 1-12.3 7.5L3.5 20.5l1.4-4.5A8.4 8.4 0 1 1 20.5 11.6z" />
    <path d="M9.2 8.6c.2-.4.5-.5.8-.5h.5c.2 0 .4.1.5.4l.6 1.5c.1.2 0 .5-.1.6l-.5.6c.6 1.1 1.4 1.9 2.5 2.5l.6-.5c.2-.2.4-.2.6-.1l1.5.6c.3.1.4.3.4.5v.5c0 .3-.1.6-.5.8-.6.3-1.4.4-2.2.1-2.2-.8-4-2.6-4.8-4.8-.3-.8-.2-1.6.1-2.2z" />
  </svg>
);

export const MapPinIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M12 21s-7-6.1-7-11.5a7 7 0 1 1 14 0C19 14.9 12 21 12 21z" />
    <circle cx="12" cy="9.5" r="2.5" />
  </svg>
);

export const ClockIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </svg>
);

export const MailIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <rect x="3" y="5" width="18" height="14" rx="1.5" />
    <path d="M3.5 6l8.5 7 8.5-7" />
  </svg>
);

export const CheckIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M5 12.5l4.5 4.5L19 7.5" />
  </svg>
);

export const UploadIcon = (props: IconProps) => (
  <svg {...defaults} {...props}>
    <path d="M12 16V4M7 9l5-5 5 5M4 20h16" />
  </svg>
);

export const StarIcon = (props: IconProps) => (
  <svg {...defaults} fill="currentColor" stroke="none" {...props}>
    <path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 16.9l-5.2 2.8 1-5.9L3.5 9.7l5.9-.8z" />
  </svg>
);
