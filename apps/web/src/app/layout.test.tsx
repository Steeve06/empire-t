import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { site } from "../test/fixtures";
import { HttpResponse, renderApp } from "../test/renderApp";

describe("layout", () => {
  it("renders the shop's details and the main navigation in French", async () => {
    renderApp("/fr/");
    expect(await screen.findByText("Ouvert 7j/7, 7h00 à 21h00")).toBeInTheDocument();
    const nav = screen.getAllByRole("navigation", { name: "Navigation principale" })[0]!;
    expect(within(nav).getByRole("link", { name: "À propos" })).toHaveAttribute(
      "href",
      "/fr/a-propos",
    );
    expect(within(nav).getByRole("link", { name: "Barbershop Hommes" })).toHaveAttribute(
      "href",
      "/fr/services/men",
    );
  });

  it("switches language to the same page", async () => {
    renderApp("/fr/");
    const toggle = await screen.findByRole("link", { name: /Read this page in English/ });
    expect(toggle).toHaveAttribute("href", "/en/");
    expect(toggle).toHaveAttribute("hreflang", "en");
  });

  it("hides the careers link once recruitment is closed", async () => {
    renderApp("/fr/", { "/api/v1/site/": { ...site, recruitment_open: false } });
    await screen.findByText("Ouvert 7j/7, 7h00 à 21h00");
    expect(screen.queryByRole("link", { name: "Recrutement" })).not.toBeInTheDocument();
  });

  it("opens and closes the mobile menu with the keyboard", async () => {
    const user = userEvent.setup();
    renderApp("/en/");
    const burger = await screen.findByRole("button", { name: "Open menu" });
    await user.click(burger);
    expect(screen.getByRole("button", { name: "Close menu" })).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    await user.keyboard("{Escape}");
    expect(screen.getByRole("button", { name: "Open menu" })).toHaveAttribute(
      "aria-expanded",
      "false",
    );
    expect(screen.getByRole("button", { name: "Open menu" })).toHaveFocus();
  });

  it("shows the 404 page for unknown URLs in the right language", async () => {
    const { unmount } = renderApp("/en/does-not-exist");
    expect(
      await screen.findByRole("heading", { level: 1, name: "Page not found" }),
    ).toBeInTheDocument();
    unmount();
    renderApp("/nowhere");
    expect(
      await screen.findByRole("heading", { level: 1, name: "Page introuvable" }),
    ).toBeInTheDocument();
  });
});

describe("home page", () => {
  it("renders the hero, popular prices and the signature package from the API", async () => {
    renderApp("/fr/");
    expect(
      await screen.findByRole("heading", { level: 1, name: "Plus qu'une coupe, une expérience." }),
    ).toBeInTheDocument();
    const popular = screen.getByRole("region", { name: "Tarifs populaires" });
    expect(within(popular).getByText("Coupe simple")).toBeInTheDocument();
    expect(within(popular).getByRole("link", { name: "Réserver : Coupe simple" })).toHaveAttribute(
      "href",
      "/fr/reserver?service=coupe-simple",
    );
    expect(screen.getByRole("heading", { name: "Empire Premium" })).toBeInTheDocument();
  });

  it("hides testimonials and gallery until the owner adds real ones", async () => {
    renderApp("/fr/");
    await screen.findByRole("region", { name: "Tarifs populaires" });
    await waitFor(() => {
      expect(screen.queryByRole("region", { name: "Nos réalisations" })).not.toBeInTheDocument();
    });
    expect(
      screen.queryByRole("region", { name: "Ce que disent nos clients" }),
    ).not.toBeInTheDocument();
  });

  it("carries the quick booking values to the booking page", async () => {
    const user = userEvent.setup();
    const { router } = renderApp("/fr/");
    const form = await screen.findByRole("form", { name: "Réservation rapide" });
    await within(form).findByRole("option", { name: "Skin Fade" });
    await user.selectOptions(within(form).getByLabelText("Service"), "skin-fade");
    await user.selectOptions(within(form).getByLabelText("Heure"), "15:30");
    await user.type(within(form).getByLabelText("Téléphone"), "653 147 512");
    await user.click(within(form).getByRole("button", { name: "Réserver" }));
    await waitFor(() => {
      expect(router.state.location.pathname).toBe("/fr/reserver");
    });
    expect(Object.fromEntries(new URLSearchParams(router.state.location.search))).toEqual({
      service: "skin-fade",
      time: "15:30",
      phone: "653 147 512",
    });
  });

  it("explains a network failure and retries", async () => {
    const user = userEvent.setup();
    let calls = 0;
    renderApp("/en/", {
      "/api/v1/site/": () => {
        calls += 1;
        return calls === 1 ? new HttpResponse(503, { detail: "Down" }) : site;
      },
    });
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("The service is briefly unavailable");
    await user.click(within(alert).getByRole("button", { name: "Try again" }));
    await waitFor(() => {
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });
  });
});
