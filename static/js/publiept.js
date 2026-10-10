/* Comportements côté navigateur de PubliEPT.
   Aucun framework : uniquement du JavaScript standard. */

/* Navigation mobile */
function basculerMenu() {
  const barre = document.getElementById('barre-laterale');
  const fond = document.getElementById('fond-menu');
  if (!barre) return;
  const ouvert = !barre.classList.contains('-translate-x-full');
  barre.classList.toggle('-translate-x-full', ouvert);
  if (fond) fond.classList.toggle('hidden', ouvert);
}

/* Menus déroulants */
function basculerMenuProfil(bouton) {
  const panneau = bouton.parentElement.querySelector('[data-panneau]');
  if (!panneau) return;
  document.querySelectorAll('[data-panneau]').forEach(function (autre) {
    if (autre !== panneau) autre.classList.add('hidden');
  });
  panneau.classList.toggle('hidden');
}

document.addEventListener('click', function (evenement) {
  if (!evenement.target.closest('[data-menu]')) {
    document.querySelectorAll('[data-panneau]').forEach(function (panneau) {
      panneau.classList.add('hidden');
    });
  }
});

/* ---- Copie dans le presse-papier ------------------------------------ */
function copierTexte(idSource, bouton) {
  const source = document.getElementById(idSource);
  if (!source) return;
  const texte = source.value !== undefined ? source.value : source.textContent;
  navigator.clipboard.writeText(texte).then(function () {
    if (!bouton) return;
    const ancien = bouton.innerHTML;
    bouton.innerHTML = 'Copié !';
    setTimeout(function () {
      bouton.innerHTML = ancien;
      if (window.lucide) lucide.createIcons();
    }, 2000);
  });
}

/* Fenêtres modales */
function ouvrirModale(id) {
  const modale = document.getElementById(id);
  if (modale) {
    modale.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}

function fermerModale(id) {
  const modale = document.getElementById(id);
  if (modale) {
    modale.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

document.addEventListener('keydown', function (evenement) {
  if (evenement.key === 'Escape') {
    document.querySelectorAll('[data-modale]:not(.hidden)').forEach(function (modale) {
      modale.classList.add('hidden');
      document.body.style.overflow = '';
    });
  }
});

/* Onglets (fenêtre « Citer ») */
function choisirFormatCitation(format, bouton) {
  document.querySelectorAll('[data-citation]').forEach(function (bloc) {
    bloc.classList.toggle('hidden', bloc.dataset.citation !== format);
  });
  document.querySelectorAll('[data-onglet-citation]').forEach(function (autre) {
    autre.classList.remove('border-blue-900', 'text-blue-900');
    autre.classList.add('border-transparent', 'text-slate-500');
  });
  bouton.classList.add('border-blue-900', 'text-blue-900');
  bouton.classList.remove('border-transparent', 'text-slate-500');
}

/* Filtrage instantané du catalogue */
/* Les filtres s'appliquent sans que l'utilisateur ait à valider :
   la soumission est déclenchée automatiquement, avec un léger délai
   pour les champs de saisie libre. */
(function () {
  const formulaire = document.getElementById('filtres-catalogue');
  if (!formulaire) return;

  let minuteur = null;
  const soumettre = function (delai) {
    clearTimeout(minuteur);
    minuteur = setTimeout(function () { formulaire.submit(); }, delai);
  };

  formulaire.querySelectorAll('select').forEach(function (champ) {
    champ.addEventListener('change', function () { soumettre(0); });
  });
  formulaire.querySelectorAll('input[type="text"], input[type="number"]').forEach(function (champ) {
    champ.addEventListener('input', function () { soumettre(450); });
  });
})();

/* Compteur de résultats */
function reinitialiserFiltres(url) {
  window.location.href = url;
}

/* Barre de chargement pour les appels IA */
function marquerChargement(bouton, message) {
  if (!bouton) return;
  bouton.disabled = true;
  bouton.dataset.ancienContenu = bouton.innerHTML;
  bouton.innerHTML = message || 'Traitement en cours…';
}

function retablirBouton(bouton) {
  if (!bouton || !bouton.dataset.ancienContenu) return;
  bouton.disabled = false;
  bouton.innerHTML = bouton.dataset.ancienContenu;
  if (window.lucide) lucide.createIcons();
}

/* Jeton CSRF */
function jetonCsrf() {
  const champ = document.querySelector('[name=csrfmiddlewaretoken]');
  return champ ? champ.value : '';
}
