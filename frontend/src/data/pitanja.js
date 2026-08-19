// Najčešća pitanja i odgovori iz oblasti zaštite i zdravlja na radu,
// preuzeta sa uznr.me/pitanja-odgovori.
export const faqs = [
  {
    id: 'pojam',
    question: 'Šta podrazumijeva zaštita i zdravlje na radu?',
    answer: [
      { type: 'text', value:
        'Zaštita i zdravlje na radu podrazumijeva obezbjeđivanje uslova na radu koji ne dovode do povreda na radu, profesionalnih bolesti i bolesti u vezi sa radom i koji stvaraju pretpostavke za punu fizičku i psihičku zaštitu zaposlenih.' },
    ],
  },
  {
    id: 'osposobljavanje',
    question: 'Kada i na koji način se obavlja osposobljavanje zaposlenih za bezbjedan rad?',
    answer: [
      { type: 'text', value:
        'Poslodavac je dužan da izvrši osposobljavanje zaposlenog kod zasnivanja radnog odnosa, raspoređivanja na drugo radno mjesto, uvođenja nove tehnologije, uvođenja novih ili zamjene sredstava za rad, promjene procesa rada i ponovnog raspoređivanja na rad poslije odsustvovanja koje je trajalo duže od godinu dana.' },
    ],
  },
  {
    id: 'prava-zaposlenih',
    question: 'Koja su prava i obaveze zaposlenih?',
    answer: [
      { type: 'text', value:
        'Zaposleni ima pravo i obavezu da se prije početka rada upozna sa mjerama zaštite i zdravlja na radu na poslovima radnog mjesta na koje je raspoređen, kao i da se osposobljava za njihovo sprovođenje. Zaposleni ima pravo i obavezu da poslodavcu daje predloge, primjedbe i obavještenja o pitanjima zaštite i zdravlja na radu. Zaposleni ima pravo i obavezu da obavi zdravstveni pregled koji odgovara riziku za zaštitu i zdravlje na radnom mjestu, na koji ga upućuje poslodavac, u skladu sa propisima o zaštiti i zdravlju na radu i propisima iz oblasti zdravstvene zaštite.' },
    ],
  },
  {
    id: 'obaveze-poslodavca',
    question: 'Koje su obaveze poslodavca?',
    answer: [
      { type: 'text', value:
        'Poslodavac je dužan da obezbijedi mjere zaštite i zdravlja na radu sprječavanjem, uklanjanjem i kontrolom rizika na radu, obavještavanjem i osposobljavanjem zaposlenih za bezbjedan i zdrav rad, uz odgovarajuću organizaciju i potrebna sredstva. Poslodavac je, takođe, dužan da se prilikom planiranja i uvođenja novih tehnologija konsultuje sa zaposlenima ili njihovim predstavnicima za zaštitu i zdravlje na radu o pitanjima izbora sredstava za rad, uslova rada, radne sredine i njihovih posljedica za zaštitu i zdravlje na radu.' },
    ],
  },
  {
    id: 'informisanje',
    question: 'Ko vrši informisanje zaposlenih o riziku i mjerama zaštite i na koji način?',
    answer: [
      { type: 'text', value:
        'Poslodavac je dužan da zaposlenog ili predstavnika zaposlenih informiše pisanim putem u vezi sa:' },
      {
        type: 'list',
        value: [
          'rizicima po zaštitu i zdravlje na radu, prevenciji, mjerama zaštite i zdravlja na radu i aktivnostima u odnosu na svaku vrstu radnog mjesta i/ili posla;',
          'načinom organizovanja i pružanja prve pomoći, zaštite od požara, postupku evakuacije zaposlenih pri pojavi ozbiljnih i neposrednih opasnosti i o licima koja su zadužena za sprovođenje ovih mjera.',
        ],
      },
    ],
  },
  {
    id: 'povreda-postupak',
    question: 'Šta treba uraditi u slučaju povrede na radu?',
    answer: [
      { type: 'text', value:
        'U slučajevima nastanka povrede na radu, zaposleni koji se zatekne na mjestu nastanka povrede, svjedok događaja, dužan je da povrijeđenom ukaže pomoć i da obavijesti prvog pretpostavljenog povrijeđenom. Ukoliko je povrijeđeni sam i svjestan, dužan je da o povredi obavijesti pretpostavljenog. Pretpostavljeni povrijeđenom je dužan da o povredi obavijesti dežurnu službu preduzeća. Dežurna služba angažuje vozača sanitetskog vozila koji preuzima medicinskog tehničara iz ambulante i ide na mjesto dešavanja povrede, radi blagovremene stručne pomoći u cilju zbrinjavanja povrijeđenog.' },
    ],
  },
  {
    id: 'prijava-povrede',
    question: 'Kome i kada poslodavac prijavljuje povredu na radu?',
    answer: [
      { type: 'text', value:
        'Poslodavac je dužan da odmah, a najkasnije u roku od 24 sata od nastanka, pisano prijavi Inspekciji rada svaku smrtnu, kolektivnu, tešku i drugu povredu na radu, koja uzrokuje odsustvo zaposlenog sa rada duže od tri radna dana, kao i opasnu pojavu koja bi mogla da ugrozi zaštitu i zdravlje zaposlenih.' },
    ],
  },
  {
    id: 'nadzor',
    question: 'Ko vrši nadzor nad sprovođenjem zaštite i zdravlja na radu?',
    answer: [
      { type: 'text', value:
        'Inspekcijski nadzor nad sprovođenjem Zakona o zaštiti i zdravlju na radu, propisa donijetih na osnovu njega i tehničkim i drugim mjerama koje se odnose na zaštitu i zdravlje na radu vrši Inspekcija rada, preko inspektora rada za oblast zaštite i zdravlja na radu.' },
    ],
  },
  {
    id: 'odbijanje-rada',
    question: 'Da li i kada zaposleni ima pravo da odbije rad?',
    answer: [
      { type: 'text', value:'Zaposleni ima pravo da odbije da radi, ako:' },
      {
        type: 'list',
        value: [
          'prethodno nije upoznat sa svim opasnostima ili štetnostima, odnosno rizicima na radu ili ako mu poslodavac nije obezbijedio propisani zdravstveni pregled;',
          'prijeti neposredna opasnost po život i zdravlje zbog toga što nijesu sprovedene propisane mjere zaštite i zdravlja na radu, sve dok se te mjere ne obezbijede;',
          'na sredstvu za rad nijesu obezbijeđene propisane mjere zaštite i zdravlja na radu i time mu je neposredno ugrožen život i zdravlje.',
        ],
      },
    ],
  },
  {
    id: 'procjena-rizika',
    question: 'Šta je akt o procjeni rizika?',
    answer: [
      { type: 'text', value:
        'Akt o procjeni rizika je akt koji sadrži opis procesa rada sa procjenom (ocjenom) rizika od povreda na radu, profesionalnih bolesti i bolesti u vezi sa radom i kojim se utvrđuju mjere zaštite i zdravlja na radu u cilju poboljšanja zaštite i zdravlja na radu.' },
      { type: 'text', value:
        'U aktu o procjeni rizika poslodavac određuje radna mjesta sa povećanim rizikom, odnosno posebnim uslovima rada, zdravstvene zahtjeve za određeni rad koje moraju da ispunjavaju zaposleni u radnom procesu ili za korišćenje pojedinih sredstava za rad na osnovu stručne ocjene ovlašćene ustanove za zdravstvenu zaštitu zaposlenih.' },
      { type: 'text', value:'Aktom iz stava 1 ovog člana utvrđuje se:' },
      {
        type: 'list',
        value: [
          'identifikacija, odnosno otkrivanje opasnosti;',
          'koja radna mjesta su izložena identifikovanim opasnostima;',
          'vjerovatnoća nastanka povrede na radu, profesionalne bolesti, odnosno bolesti u vezi sa radom;',
          'da li je rizik prihvatljiv;',
          'uvođenje mjera za smanjenje neprihvatljivog rizika.',
        ],
      },
    ],
  },
  {
    id: 'posebni-uslovi',
    question: 'Šta su radna mjesta sa posebnim uslovima rada?',
    answer: [
      { type: 'text', value:
        'Radna mjesta sa posebnim uslovima rada su radna mjesta na koja mogu biti raspoređeni i obavljati poslove tih radnih mjesta samo zaposleni koji, pored opštih uslova za zasnivanje radnog odnosa, ispunjavaju i posebne uslove u pogledu pola, godina života, školske spreme, stručne osposobljenosti, zdravstvenog stanja i psihičkih sposobnosti.' },
      { type: 'text', value:
        'Poslodavac ne može rasporediti zaposlenog da radi na radnom mjestu sa posebnim uslovima rada, ukoliko prethodno nije utvrdio da zaposleni ispunjava propisane posebne uslove.' },
    ],
  },
]
