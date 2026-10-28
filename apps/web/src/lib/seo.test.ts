import { describe, expect, it } from "vitest";

import { buildHead, renderHeadHtml, safeJson } from "./seo";

describe("buildHead", () => {
  const head = buildHead(
    { title: "Contact", description: "Écrivez-nous" },
    "fr",
    "/fr/contact",
    "Empire T Barbershop & Beauty",
    "Default",
  );

  it("titles the page and points canonical and hreflang at both languages", () => {
    expect(head.title).toBe("Contact | Empire T Barbershop & Beauty");
    expect(head.canonical).toMatch(/\/fr\/contact$/);
    expect(head.alternates.map((alt) => [alt.hreflang, new URL(alt.href).pathname])).toEqual([
      ["fr", "/fr/contact"],
      ["en", "/en/contact"],
      ["x-default", "/fr/contact"],
    ]);
    expect(head.ogLocale).toBe("fr_CM");
  });

  it("escapes values when rendering HTML", () => {
    const html = renderHeadHtml({ ...head, description: 'Say "hi" <b>' }, []);
    expect(html).toContain('content="Say &quot;hi&quot; &lt;b&gt;"');
  });
});

describe("safeJson", () => {
  it("cannot close the surrounding script element", () => {
    const json = safeJson({ text: "</script><script>alert(1)</script>" });
    expect(json).not.toContain("</script>");
    expect(JSON.parse(json)).toEqual({ text: "</script><script>alert(1)</script>" });
  });
});
