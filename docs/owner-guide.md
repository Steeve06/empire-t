# Guide du gérant · Empire T

Ce guide explique comment gérer le site sans développeur : prix, prestations, photos, réservations, candidatures et messages. Tout se fait dans l'**administration**, à l'adresse `https://votre-domaine/admin/`, depuis un ordinateur ou un téléphone.

> **Ce que vous modifiez est visible tout de suite** par les visiteurs. Les pages lues par Google se mettent à jour automatiquement dans l'heure.

## Sommaire

1. [Se connecter](#1-se-connecter)
2. [Changer un prix](#2-changer-un-prix)
3. [Ajouter, retirer ou réordonner une prestation](#3-ajouter-retirer-ou-réordonner-une-prestation)
4. [Photos : galerie et photos du site](#4-photos--galerie-et-photos-du-site)
5. [Réservations](#5-réservations)
6. [Recrutement et candidatures](#6-recrutement-et-candidatures)
7. [Messages de contact](#7-messages-de-contact)
8. [Avis clients et équipe](#8-avis-clients-et-équipe)
9. [Paramètres du site](#9-paramètres-du-site)
10. [Textes en anglais](#10-textes-en-anglais)
11. [Sécurité et bonnes pratiques](#11-sécurité-et-bonnes-pratiques)

---

## 1. Se connecter

1. Ouvrez `https://votre-domaine/admin/`.
2. Entrez votre identifiant et votre mot de passe.
3. La page d'accueil de l'administration liste toutes les rubriques : **Prestations et tarifs**, **Réservations**, **Recrutement**, **Galerie**, **Messages**, **Site**.

Mot de passe oublié ? Demandez à la personne qui gère le serveur de le réinitialiser (voir le guide de déploiement).

## 2. Changer un prix

Le plus rapide, directement dans la liste :

1. **Prestations et tarifs › Prestations**.
2. Filtrez par catégorie à droite (Hommes, Femmes…), ou cherchez le nom en haut.
3. Modifiez la colonne **prix (FCFA)** sur la ligne voulue. Écrivez le nombre sans espace : `2500`.
4. Cliquez sur **Enregistrer** en bas de la liste.

Les cases de la même liste servent aussi à :

| Case | Effet sur le site |
|---|---|
| **prix « dès »** | Affiche « dès 3 000 F » au lieu de « 3 000 F » |
| **tarif populaire** | Place la prestation dans « Tarifs populaires » sur l'accueil (gardez-en 4) |
| **active** | Décochée : la prestation disparaît du site sans être supprimée |
| **ordre** | Position dans la liste (1 en premier) |

**Prix sur devis** (ex. « Locks complexes ») : ouvrez la prestation, cochez **sur devis** et laissez le prix vide. Le site affiche « Sur devis ».

**Suppléments** (massage du cuir chevelu, serviette chaude…) : **Prestations et tarifs › Suppléments**, même fonctionnement.

## 3. Ajouter, retirer ou réordonner une prestation

**Ajouter** : **Prestations › Ajouter prestation** (bouton en haut à droite), puis remplissez :

- **catégorie** (Hommes, Femmes, Enfants, Beauty & Spa, Barbe & Packs) ;
- **nom [fr]** et **nom [en]** (voir [Textes en anglais](#10-textes-en-anglais)) ;
- **durée minimale** et, si la durée varie, **durée maximale** (en minutes) ;
- **prix (FCFA)** ;
- une **description** courte si utile.

L'identifiant d'URL se remplit tout seul. Enregistrez : la prestation apparaît sur la page Services et dans le formulaire de réservation.

**Retirer** : décochez **active** plutôt que supprimer. Les anciennes réservations gardent ainsi leur historique.

**La prestation signature** (« Empire Premium » sur l'accueil) se choisit dans **Site › Paramètres du site › Photos et forfait signature**.

**Les catégories** (Prestations et tarifs › Catégories) permettent de changer le titre, la phrase d'accroche, la mention « Sur rendez-vous », la photo, l'ordre des onglets et l'affichage sur l'accueil (**afficher sur l'accueil**).

## 4. Photos : galerie et photos du site

**Formats acceptés** : JPEG, PNG ou WebP, 12 Mo maximum. Depuis un iPhone, envoyez la photo depuis le navigateur : elle est normalement convertie en JPEG. Sinon, réglez l'appareil photo sur « Le plus compatible » (Réglages › Appareil photo › Formats). Le site redimensionne et compresse chaque photo automatiquement pour qu'elle s'affiche vite sur les téléphones. Inutile de la retoucher avant.

### Ajouter une photo à la galerie

1. **Galerie › Ajouter photo de la galerie**.
2. Choisissez le fichier.
3. **Catégorie** : Coupes, Coiffures, Beauty ou Le salon (ce sont les filtres de la page Galerie).
4. **Description de la photo [fr] / [en]** : obligatoire. Décrivez ce qu'on voit, par exemple « Skin fade avec motif ». Elle est lue aux personnes malvoyantes et aide Google.
5. **Légende** (facultatif) : texte affiché sur la photo.
6. **Sur l'accueil** : cochez pour la montrer dans l'aperçu de la page d'accueil (6 photos).
7. **Prestation liée** (facultatif) : le bouton « Réserver ce style » ouvrira la réservation avec cette prestation déjà choisie.

Pour masquer une photo sans la supprimer, décochez **publiée**.

### Photos du site

Dans **Site › Paramètres du site › Photos et forfait signature** :

- **photo principale** : la grande photo de l'accueil ;
- **photo du forfait signature** : la section « Notre signature » ;
- **photo À propos** : la page À propos.

Chaque catégorie, prestation et membre de l'équipe a aussi son champ **photo**. Tant qu'une photo manque, le site affiche un cadre sombre élégant avec « Photo à venir ».

## 5. Réservations

Quand un client réserve sur le site :

1. la demande est enregistrée ici avec le statut **Nouvelle** et une référence (ex. `ET-3WF9H2`) ;
2. le client est envoyé sur WhatsApp avec un message prérempli contenant la prestation, la date, l'heure, son nom et la référence ;
3. **vous confirmez sur WhatsApp**, puis mettez à jour le statut ici.

Dans **Réservations › Demandes de réservation** :

- filtrez par **statut**, **date** ou **catégorie** à droite, ou cherchez une référence, un nom ou un numéro ;
- cochez une ou plusieurs demandes, puis choisissez une action en haut : **Marquer comme confirmées**, **honorées**, **annulées**, **absents** ;
- **Exporter la sélection (CSV)** ouvre la liste dans Excel ou Google Sheets.

Aucun paiement n'est demandé en ligne : le client règle au salon (espèces ou Mobile Money).

Les créneaux proposés vont de l'ouverture à la fermeture, toutes les 30 minutes, jusqu'à 60 jours à l'avance. Ces réglages sont dans **Paramètres du site › Horaires et réservations**.

## 6. Recrutement et candidatures

### Les offres

**Recrutement › Offres d'emploi** : titre, **nombre de postes**, exigences et description, en français et en anglais. Décochez **active** pour retirer une offre.

La **date limite** générale se règle dans **Paramètres du site › Recrutement**, avec la liste des documents demandés (un document par ligne). Une offre peut avoir sa propre date limite, plus courte.

**Après la date limite**, le site retire automatiquement le lien « Recrutement », la bannière de l'accueil et le formulaire. La page affiche alors que les candidatures sont closes. Pour un nouveau recrutement, repoussez la date limite.

### Les candidatures

Chaque candidature envoyée vous parvient aussi par email (voir **email de notification** dans les paramètres).

Dans **Recrutement › Candidatures**, ouvrez une candidature pour voir les coordonnées et **télécharger chaque fichier** (CV, CNI, photos, vidéos). Ces fichiers sont privés : ils ne sont jamais accessibles par une adresse publique.

Actions disponibles : **en cours d'examen**, **entretien prévu**, **non retenue**, **recruté(e)**, et **Exporter la sélection (CSV)**.

## 7. Messages de contact

**Messages › Messages de contact** liste les messages du formulaire Contact, qui arrivent aussi par email. Le lien dans la colonne contact ouvre directement WhatsApp ou votre messagerie pour répondre. Actions : **Marquer comme lus**, **répondus**, **Archiver**.

## 8. Avis clients et équipe

Ces sections restent **masquées sur le site tant qu'elles sont vides**. Nous n'avons volontairement inventé aucun avis ni aucun membre d'équipe.

- **Site › Témoignages** : ajoutez de vrais avis de clients, avec leur accord (nom, quartier, texte en français et en anglais, note sur 5). L'accueil en affiche trois. Décochez **publié** pour en retirer un.
- **Site › Équipe** : nom, rôle, courte présentation, photo. Visible sur la page À propos.

## 9. Paramètres du site

**Site › Paramètres du site** (une seule fiche) :

| Section | Contenu |
|---|---|
| Identité | Nom, sous-titre, slogan (« Plus qu'une coupe, une expérience. ») |
| Contact | **Numéro WhatsApp** au format international `+237653147512` (il sert à tous les liens WhatsApp et aux réservations), email public, **email de notification**, Mobile Money accepté |
| Adresse et carte | Adresse, ville, position sur la carte (latitude, longitude) et **lien Google Maps** |
| Horaires et réservations | Ouverture, fermeture, jours, intervalle des créneaux, délai maximum de réservation |
| Réseaux sociaux | Liens Instagram, Facebook, TikTok (affichés en pied de page dès qu'ils sont remplis) |
| Recrutement | Date limite, documents demandés |
| Page À propos | Histoire du salon, équipements (une ligne par équipement) |
| Photos et forfait signature | Photos principales, prestation signature |

**À faire avant le lancement :**

- remplacer l'email `contact@empire-t.cm` par votre vraie adresse ;
- placer le repère exact du salon : dans Google Maps, faites un appui long sur le salon, copiez les deux nombres affichés (latitude, longitude) dans les champs correspondants, puis collez le lien de partage dans **lien Google Maps**.

## 10. Textes en anglais

Les champs traduits apparaissent par paires : **nom [fr]** et **nom [en]**, **description [fr]** et **description [en]**… Le site anglais (`/en/`) utilise la version [en]. Si elle est vide, le texte français s'affiche à la place : rien n'est jamais vide pour le visiteur.

## 11. Sécurité et bonnes pratiques

- Utilisez un mot de passe long et unique. Changez-le via **Modifier le mot de passe**, en haut à droite.
- Créez un compte par personne (**Authentification › Utilisateurs**) plutôt que partager le vôtre. Un employé qui ne gère que les réservations peut recevoir des droits limités à cette rubrique.
- Ne supprimez rien que vous pourriez vouloir retrouver : décochez **active** ou **publiée**.
- Les données sont sauvegardées chaque nuit. Une erreur se rattrape, demandez simplement une restauration.

**Une question, un problème ?** Contactez la personne en charge du serveur. Le guide technique est dans `docs/deployment.md`.
