# Priprema za produkciju

Šta mora biti urađeno prije nego što uznr.me proradi kao pravi sajt, a ne kao
demo. Poređano po prioritetu: bez prve sekcije administracija se ne može
koristiti za stvarni rad.

Sve je u jednom repozitorijumu, ali se objavljuje na dva mjesta — svaka usluga
gleda samo svoj direktorijum:

| Dio | Direktorijum | Server | Podešavanje |
| --- | --- | --- | --- |
| Frontend (Vue) | `frontend/` | Netlify — https://uznr.netlify.app | `netlify.toml` (`base`) |
| Backend (Django) | `backend/` | Render (besplatni plan) | `render.yaml` (`rootDir`) |

---

## 1. Blokirajuće — bez ovoga sajt ne radi kako treba

### Prava baza podataka

Besplatni Render plan daje privremeni disk, pa se **`backend/db.sqlite3` briše pri
svakoj novoj objavi**. Sve što se unese u administraciju na sajtu nestaje čim se
backend ponovo objavi. Zbog toga je `ADMIN_READONLY` postavljen na `"True"` u
`render.yaml`: nalog može da gleda, ali ne i da čuva, kako niko ne bi izgubio
posao za koji misli da je sačuvan.

Dok ne postoji trajna baza, administracija na sajtu je samo demonstracija.
Postupak:

1. Dodati Postgres bazu (Render ima svoju, može i bilo koji drugi provajder).
2. Usmjeriti `DATABASES` na nju — obično preko `DATABASE_URL` i biblioteke
   `dj-database-url`. Trenutno je u `backend/config/settings.py` zakucan SQLite, a
   `dj-database-url` **nije** u `backend/requirements.txt`, pa ga treba dodati.
3. Pokrenuti migracije, pa jednom `python manage.py import_seed` (iz `backend/`) da se učita
   početni sadržaj.
4. Tek tada postaviti `ADMIN_READONLY=False`.

Redoslijed je bitan. Ako se prvo isključi `ADMIN_READONLY`, izmjene se neće
blokirati — nego će se tiho gubiti.

### Podaci za prijavu na administraciju

`backend/content/management/commands/ensure_admin_user.py` podrazumijevano pravi nalog **`admin` / `123`**, a ta
lozinka se nalazi u javnom repozitorijumu. To je bio svjestan ustupak — besplatni
Render plan nema konzolu, pa bez podrazumijevanih vrijednosti administracija na
sajtu ne bi imala nijedan nalog, a nalog i tako može samo da gleda.

Čim administracija bude mogla da čuva izmjene, to više nije prihvatljivo:

- Postaviti `ADMIN_USERNAME`, `ADMIN_PASSWORD` i `ADMIN_EMAIL` u Render panelu
  (označeni su sa `sync: false`, pa ih nema u repozitorijumu).
- Koristiti pravu lozinku, ne varijaciju na `123`.
- Tek onda postaviti `ADMIN_READONLY=False`.

### Slanje mejlova sa kontakt forme

Ako `EMAIL_HOST` nije postavljen, `backend/config/settings.py` namjerno koristi Django konzolni
način rada: mejl se **ispisuje, a ne šalje**. Poruke se i dalje čuvaju i vide u
dijelu *Sanduče*, ali:

- pošiljalac ne dobija potvrdu, i
- niko ne biva obaviješten da je poruka stigla.

`EMAIL_HOST`, `EMAIL_HOST_USER` i `EMAIL_HOST_PASSWORD` su `sync: false`, pa se
jedino u Render panelu vidi da li su popunjeni — **provjeriti da jesu.** Dvije
stvari moraju biti tačne:

- `DEFAULT_FROM_EMAIL` mora biti adresa sa koje SMTP nalog smije da šalje, inače
  provajderi odbijaju poruku ili je svrstavaju u nepoželjnu poštu.
- `CONTACT_NOTIFY_EMAILS` je adresa na koju se poruke prosljeđuju
  (`info@uznr.me`).

Provjera: popuniti formu na objavljenom sajtu i potvrditi da stižu oba mejla —
potvrda pošiljaocu i kopija Udruženju.

---

## 2. Prije zvaničnog objavljivanja

### Sadržaj

Provjereno nad stvarnim podacima (170 vijesti, 7 oglasa, 45 članova):

- **Četiri naslova napisana velikim slovima.** Frontend ih automatski vraća u
  normalan oblik, ali ne može da povrati vlastita imena — „BIJELO POLJE“ postaje
  „Bijelo polje“. Ispraviti ih u administraciji:
  - `SASTANAK SA MLADIM AMBASADORIMA DOSTOJANSTVENOG RADA…`
  - `EDUKATIVNA RADIONICA U JU SREDNJA ELEKTRO-EKONOMSKA ŠKOLA…`
  - `POZIV ZA UČEŠĆE NA EDUKATIVNO-ZAGOVARAČKOJ RADIONICI`
  - `POZIV ZA MEDIJSKE ORGANIZACIJE/NOVINARE ZA UČEŠĆE…`
- **Četiri vijesti dijele isti naslov** („Realizovana obuka: Zaštita i zdravlje
  na radu u sistemu vaspitanja i obrazovanja“). To **nisu** duplikati — riječ je
  o četiri različite obuke (8, 15, 24. i 25. decembra 2025), svaka sa svojim
  tekstom i svojom adresom. Problem je samo što se u spiskovima i u pretrazi ne
  razlikuju. Dodati mjesto ili datum u naslov.
- **Pet od sedam oglasa nema datum objave.** U administraciji stoji „-“, a na
  sajtu se datum jednostavno ne prikazuje. Popuniti ih da bi se oglasi mogli
  ispravno ređati.
- **Nijedan od 45 članova nema veb adresu.** Polje postoji i kolona „Veb adresa“
  je vidljiva u administraciji, ali su sva prazna, pa nijedan logotip na
  početnoj strani nije klikabilan.
- **Petnaest od 170 vijesti nema naslovnu fotografiju.** Prikazuju se sa praznim
  poljem umjesto slike.

Provjereno i uredno: nema duplikata (ni naslova, ni adresa, ni članova), sve
unutrašnje veze rade (367 provjerenih), sve slike se učitavaju (326), svih osam
spoljnih linkova vraća 200, a crnogorska i engleska verzija imaju isti broj
ključeva (294).

### Autorska prava

Ilustracije na stranicama Publikacije, Pitanja & Odgovori, Kontakt i na stranici
za nepostojeću adresu preuzete su sa [Storyset](https://storyset.com/), čija
besplatna licenca **zahtijeva vidljivo navođenje autora**. To navođenje stoji u
podnožju sajta („Ilustracije: Storyset“). Ne uklanjati ga osim ako se licenca ne
otkupi.

### Instagram

`frontend/scripts/fetch-instagram.mjs` se izvršava pri izradi sajta i traži važeći token.
Instagram tokeni traju oko 60 dana; obnoviti ih komandom
`npm run refresh-instagram-token` prije isteka, inače Instagram sekcija ostaje
zastarjela.

---

## 3. Poznata ograničenja

- **Dugme za prikaz na telefonu i tabletu.** Plutajuće dugme koje otvara sajt u
  prozoru veličine telefona ili tableta je alat za izradu sajta, a ne nešto što
  posjetilac treba da vidi. Sada se učitava **samo pri radu na računaru** i u
  objavljenoj verziji ga nema — provjereno: ni komponenta, ni njeni stilovi, ni
  spisak uređaja ne postoje u objavljenim datotekama. Ako se nikada više neće
  koristiti, mogu se obrisati i sami fajlovi:
  `frontend/src/components/DevicePreviewSwitch.vue`,
  `frontend/src/devicePreview.js` i njihovi
  prevodi pod `devicePreview` u oba jezika.
- **Prvo učitavanje je sporo.** Besplatni Render plan gasi backend nakon oko 15
  minuta neaktivnosti, pa prvi sljedeći zahtjev može trajati do minut. Frontend
  to već rješava: stranice se prikazuju iz ugrađenih podataka i ispisuju
  obavještenje da se server pokreće.

---

## 4. Poslije svake objave provjeriti

- Sajt se učitava i vijesti se prikazuju (računati na sporo prvo učitavanje).
- Izmišljena adresa, na primjer `/nesto-nepostojece`, prikazuje uređenu stranicu
  s porukom da stranica nije pronađena, a ne praznu stranicu.
- Pretraga nalazi riječi napisane bez kvačica: `zastita` treba da da iste
  rezultate kao `zaštita`.
- Kontakt forma šalje poruku i oba mejla stižu.
- `/admin/` se otvara, a dugme „Pogledaj sajt“ u zaglavlju vodi na javni sajt
  (čita se iz `SITE_URL`).

---

## Samo za rad na računaru (ne tiče se produkcije)

Ako se backend pokreće na Windowsu: bez postavljenog `EMAIL_HOST` Django ispisuje
mejl u konzolu, a `cp1252` konzola ne može da ispiše slovo `ć`, pa slanje potvrde
puca sa `UnicodeEncodeError` i administracija javlja „Slanje nije uspjelo“. Zato
pokretati razvojni server ovako:

```sh
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python manage.py runserver
```
