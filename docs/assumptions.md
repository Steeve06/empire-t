# Assumptions

Made where the brief was silent. Each one is editable without a developer unless noted.

| # | Assumption | Where to change it |
|---|---|---|
| A1 | Public email is `contact@empire-t.cm` and receives application and contact notifications. **Replace before launch**: notifications to a non-existent mailbox are lost (submissions are still saved in the admin). | Admin › Paramètres du site › Contact |
| A2 | Map pin at latitude 3.8935, longitude 11.5440 (approximate Nkolmesseng). The exact spot "axe principal, à côté du carrefour" needs the owner's coordinates or a Google Maps share link. | Admin › Paramètres du site › Adresse et carte |
| A3 | « Locks complexes, sur devis » takes 120 to 240 minutes. | Admin › Prestations |
| A4 | Booking slots every 30 minutes, 7h00 to 21h00, a service must end by closing time, at least 30 minutes' notice, up to 60 days ahead. | Admin › Paramètres du site › Horaires et réservations |
| A5 | "Tarifs populaires" shows Coupe simple, Low/Mid/High Fade, Coupe + barbe and Nattes / Cornrows (the four rows of the prototype). | Admin › Prestations › « tarif populaire » |
| A6 | The home page shows four category cards (Hommes, Femmes, Enfants, Beauty & Spa); Barbe & Packs is reachable through the menu and Services tabs. | Admin › Catégories › « afficher sur l'accueil » |
| A7 | No testimonials, team members or photos are seeded. Inventing customer reviews or staff would be misleading; the frontend hides those sections until the owner adds real content. | Admin › Témoignages / Équipe / Galerie |
| A8 | Application titles are singular ("Barber titulaire") with the count shown separately ("2 postes"). "Titulaire" is translated as *permanent*, "remplaçant(e)" as *relief*. | Admin › Offres d'emploi |
| A9 | One recruitment deadline (15 novembre 2026) applies to all openings; an opening may set an earlier one. After the deadline the openings list is empty and the frontend hides the Recrutement page and CTA. | Admin › Paramètres du site › Recrutement |
| A10 | Booking requests from the website arrive with status « Nouvelle »; the owner confirms on WhatsApp and updates the status in the admin. No automatic email is sent for bookings (WhatsApp is the channel). | Code: `apps/bookings` |
| A11 | Customer phone numbers are Cameroonian (9 digits starting with 6 or 2, with or without +237) or any international number written with `+`. | Code: `apps/core/validators.py` |
| A12 | Shop notification emails are written in French whatever the visitor's language. | Code: `apps/core/notifications.py` |
| A13 | Production runs on a single small VPS (Docker Compose, Postgres and Redis on the same host). S3-compatible storage is optional and switched on with `USE_S3=true`. | `.env` |
| A14 | The brief says Python 3.12; images use 3.12. The code also runs on 3.13 (used in local verification). | `infra/api.Dockerfile` |
| A15 | Hero paragraph, the four values (Qualité, Propreté, Rapidité, Style) and other interface copy are fixed text in both languages; the tagline, prices, categories, story and everything the owner manages come from the API. | Code: `apps/web/src/i18n/fr.ts`, `en.ts` |
| A16 | Visiting `/` opens the French site unless the browser asks for English and not French. | Code: `infra/nginx`, `apps/web/src/app/LanguageRedirect.tsx` |
| A17 | The logo is a typographic wordmark (EMPIRE T / BARBERSHOP & BEAUTY) until the owner's crown-and-shield files arrive; labelled placeholders stand in for every photo not yet uploaded. | `apps/web/src/components/layout/Logo.tsx`, Admin › photos |
| A18 | Social links (Instagram, Facebook, TikTok) appear in the footer only once a URL is filled in; none were provided. | Admin › Paramètres du site › Réseaux sociaux |
| A19 | Prices display as « 3 500 F » (French) and "3,500 F" (English), CFA franc with a non-breaking space; the services page states that all prices are in FCFA. | Code: `apps/web/src/lib/format.ts` |
