import { useCallback, type HTMLAttributes } from "react";

type RevealTag = "div" | "section" | "li" | "article";

/**
 * Fades content up as it scrolls into view. Elements already on screen when the
 * page hydrates are left alone, so pre-rendered content never blinks or delays LCP.
 */
export function Reveal({
  as: Tag = "div",
  ...props
}: { as?: RevealTag } & HTMLAttributes<HTMLElement>) {
  const ref = useCallback((element: HTMLElement | null) => {
    if (!element || typeof IntersectionObserver === "undefined") return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (element.getBoundingClientRect().top < window.innerHeight) return;

    element.classList.add("reveal-pending");
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry?.isIntersecting) return;
        element.classList.replace("reveal-pending", "reveal-shown");
        observer.disconnect();
      },
      { rootMargin: "0px 0px -8% 0px" },
    );
    observer.observe(element);
    return () => {
      observer.disconnect();
    };
  }, []);

  return <Tag ref={ref} {...props} />;
}
