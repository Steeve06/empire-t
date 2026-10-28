import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import type { GalleryImage } from "@empire-t/api-client";

import { openings, site } from "../test/fixtures";
import { HttpResponse, renderApp } from "../test/renderApp";

const photo = (
  id: number,
  category: GalleryImage["category"],
  service: string | null = null,
): GalleryImage => ({
  id,
  category,
  alt_text: `Photo ${id}`,
  caption: `Légende ${id}`,
  service,
  is_featured: true,
  image: { src: `/media/${id}.webp`, srcset: `/media/${id}.webp 480w`, width: 480, height: 600 },
});

describe("services page", () => {
  it("shows the tab from the URL and links every row to the booking page", async () => {
    renderApp("/fr/services/women");
    const tabs = await screen.findByRole("navigation", { name: "Catégories de services" });
    expect(within(tabs).getByRole("link", { name: "Femmes" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByText("Sur rendez-vous")).toBeInTheDocument();
    expect(screen.getByText("Sur devis")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Réserver : Retwist" })).toHaveAttribute(
      "href",
      "/fr/reserver?service=retwist",
    );
    expect(await screen.findByText(/Serviette chaude/)).toBeInTheDocument();
  });

  it("defaults to the first category and switches tabs through the URL", async () => {
    const user = userEvent.setup();
    const { router } = renderApp("/en/services");
    expect(await screen.findByText("Skin Fade")).toBeInTheDocument();
    // Fixtures hold the French content; the interface around it is English.
    const tabs = screen.getByRole("navigation", { name: "Service categories" });
    await user.click(within(tabs).getByRole("link", { name: "Enfants" }));
    expect(router.state.location.pathname).toBe("/en/services/kids");
    expect(await screen.findByText("Coupe enfant, jusqu'à 12 ans")).toBeInTheDocument();
  });

  it("says so for an unknown category", async () => {
    renderApp("/fr/services/inconnu");
    expect(await screen.findByText("Cette catégorie n'existe pas.")).toBeInTheDocument();
  });
});

describe("gallery page", () => {
  it("shows an empty state until photos are uploaded", async () => {
    renderApp("/fr/galerie");
    expect(await screen.findByText(/Les photos arrivent bientôt/)).toBeInTheDocument();
  });

  it("filters, opens the lightbox and books the photo's style", async () => {
    const user = userEvent.setup();
    const all = [photo(1, "cuts", "skin-fade"), photo(2, "beauty")];
    renderApp("/fr/galerie", {
      "/api/v1/gallery/": (request: Request) => {
        const category = new URL(request.url).searchParams.get("category");
        const results = category ? all.filter((item) => item.category === category) : all;
        return { count: results.length, next: null, previous: null, results };
      },
    });
    await user.click(await screen.findByRole("button", { name: "Agrandir : Photo 1" }));
    const dialog = screen.getByRole("dialog", { name: "Photo 1" });
    expect(within(dialog).getByText("1 sur 2")).toBeInTheDocument();
    expect(within(dialog).getByRole("link", { name: "Réserver ce style" })).toHaveAttribute(
      "href",
      "/fr/reserver?service=skin-fade",
    );
    await user.click(within(dialog).getByRole("button", { name: "Photo suivante" }));
    expect(within(screen.getByRole("dialog")).getByText("2 sur 2")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Beauty", hidden: true }));
    await waitFor(() => {
      expect(screen.queryByRole("button", { name: "Agrandir : Photo 1" })).not.toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: "Beauty" })).toHaveAttribute("aria-pressed", "true");
  });
});

describe("booking page", () => {
  const tomorrow = new Date(Date.now() + 86_400_000).toISOString().slice(0, 10);
  const slots = { "/api/v1/bookings/slots/": { date: tomorrow, slots: ["09:00", "09:30"] } };

  it("validates in the page's language before sending anything", async () => {
    const user = userEvent.setup();
    const { fetch } = renderApp("/en/book", slots);
    await user.click(await screen.findByRole("button", { name: "Send on WhatsApp" }));
    expect(await screen.findByText("Please fix the highlighted fields.")).toBeInTheDocument();
    expect(screen.getAllByText("This field is required.").length).toBeGreaterThanOrEqual(4);
    expect(fetch.mock.calls.some(([input]) => (input as Request).method === "POST")).toBe(false);
  });

  it("books a prefilled service and shows the WhatsApp confirmation", async () => {
    const user = userEvent.setup();
    let sent: Record<string, unknown> = {};
    renderApp(
      `/fr/reserver?service=skin-fade&date=${tomorrow}&time=09:30&phone=653147512&via=quick`,
      {
        ...slots,
        "/api/v1/bookings/": async (request: Request) => {
          sent = (await request.clone().json()) as Record<string, unknown>;
          return new HttpResponse(201, {
            reference: "ET-ABC123",
            status: "new",
            service: "skin-fade",
            service_name: "Skin Fade",
            date: tomorrow,
            time_slot: "09:30",
            customer_name: "Awa",
            whatsapp_url: "https://wa.me/237653147512?text=Bonjour",
          });
        },
      },
    );
    const name = await screen.findByLabelText("Votre nom");
    await waitFor(() => {
      expect(screen.getByLabelText("Heure")).toHaveValue("09:30");
    });
    await user.type(name, "Awa");
    await user.click(screen.getByRole("button", { name: "Envoyer sur WhatsApp" }));

    expect(await screen.findByRole("heading", { name: "Demande enregistrée" })).toBeInTheDocument();
    expect(screen.getByText("Référence ET-ABC123")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Ouvrir WhatsApp/ })).toHaveAttribute(
      "href",
      "https://wa.me/237653147512?text=Bonjour",
    );
    expect(screen.getByRole("img", { name: /QR code/ })).toBeInTheDocument();
    expect(sent).toMatchObject({
      service: "skin-fade",
      date: tomorrow,
      time_slot: "09:30",
      customer_name: "Awa",
      phone: "653147512",
      channel: "quick_bar",
      website: "",
    });
  });

  it("shows the API's refusal next to the field it concerns", async () => {
    const user = userEvent.setup();
    renderApp(`/fr/reserver?service=skin-fade&date=${tomorrow}&time=09:00&phone=653147512`, {
      ...slots,
      "/api/v1/bookings/": new HttpResponse(400, {
        time_slot: ["Ce créneau n'est pas disponible. Choisissez une autre heure."],
      }),
    });
    await user.type(await screen.findByLabelText("Votre nom"), "Awa");
    await waitFor(() => {
      expect(screen.getByLabelText("Heure")).toHaveValue("09:00");
    });
    await user.click(screen.getByRole("button", { name: "Envoyer sur WhatsApp" }));
    expect(await screen.findByText(/Ce créneau n'est pas disponible/)).toBeInTheDocument();
    expect(screen.getByLabelText("Heure")).toHaveAttribute("aria-invalid", "true");
  });
});

describe("careers page", () => {
  it("lists the openings and required documents", async () => {
    renderApp("/fr/recrutement");
    expect(await screen.findByRole("heading", { name: "Barber titulaire" })).toBeInTheDocument();
    expect(screen.getByText("2 postes")).toBeInTheDocument();
    expect(screen.getByText("Copie de la CNI")).toBeInTheDocument();
  });

  it("sends an application with its files", async () => {
    const user = userEvent.setup({ applyAccept: false });
    let form: FormData | undefined;
    renderApp("/fr/recrutement", {
      "/api/v1/careers/applications/": async (request: Request) => {
        form = await request.clone().formData();
        return new HttpResponse(201, { detail: "Candidature envoyée." });
      },
    });
    await user.selectOptions(await screen.findByLabelText("Poste"), openings[0]!.slug);
    await user.type(screen.getByLabelText("Nom complet"), "Paul Mbarga");
    await user.type(screen.getByLabelText("Email ou WhatsApp"), "paul@mail.cm");
    const input = screen.getByLabelText("Documents", { selector: "input" });
    await user.upload(input, new File(["%PDF"], "virus.exe"));
    expect(screen.getByText(/virus.exe : format non accepté/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Retirer virus.exe" }));
    await user.upload(input, [new File(["%PDF"], "cv.pdf"), new File(["img"], "cni.jpg")]);
    await user.click(screen.getByRole("button", { name: "Envoyer ma candidature" }));

    expect(await screen.findByRole("heading", { name: "Candidature envoyée" })).toBeInTheDocument();
    expect(form?.get("opening")).toBe(openings[0]!.slug);
    // jsdom drops file names in multipart bodies; the API client test checks them in Node.
    expect(form?.getAll("files")).toHaveLength(2);
  });

  it("closes itself once recruitment is over", async () => {
    renderApp("/en/careers", {
      "/api/v1/site/": { ...site, recruitment_open: false },
      "/api/v1/careers/openings/": [],
    });
    expect(
      await screen.findByRole("heading", { level: 1, name: "Applications are closed" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Send my application" })).not.toBeInTheDocument();
  });
});

describe("contact page", () => {
  it("sends a message and confirms it", async () => {
    const user = userEvent.setup();
    renderApp("/en/contact", {
      "/api/v1/contact/": new HttpResponse(201, { detail: "Thank you!" }),
    });
    expect(await screen.findByRole("link", { name: "653 147 512" })).toHaveAttribute(
      "href",
      site.whatsapp_url,
    );
    await user.type(screen.getByLabelText("Name"), "Awa");
    await user.type(screen.getByLabelText("Phone or email"), "awa@mail");
    await user.type(screen.getByLabelText("Message"), "Hello");
    await user.click(screen.getByRole("button", { name: "Send" }));
    expect(
      await screen.findByText("Enter a valid email address or phone number."),
    ).toBeInTheDocument();
    expect(screen.getByText("Your message must be at least 10 characters.")).toBeInTheDocument();

    await user.clear(screen.getByLabelText("Phone or email"));
    await user.type(screen.getByLabelText("Phone or email"), "awa@mail.cm");
    await user.type(screen.getByLabelText("Message"), " from Bastos, do you braid on Sundays?");
    await user.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByRole("heading", { name: "Message sent" })).toBeInTheDocument();
  });
});

describe("about page", () => {
  it("tells the story and lists the amenities", async () => {
    renderApp("/fr/a-propos");
    expect(await screen.findByText(/Empire T est né d'une idée simple/)).toBeInTheDocument();
    expect(screen.getByText("Wi-Fi gratuit")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Notre équipe" })).not.toBeInTheDocument();
  });
});
