// ============================================================
// APHPM — Script JavaScript principal
// ============================================================

// ============================================================
// MENU HAMBURGER (Mobile)
// ============================================================

/**
 * Ouvre ou ferme le menu mobile
 * Appelée par onclick="toggleMenu()" dans le HTML
 */
function toggleMenu() {
  // Ajoute/retire la classe "open" sur le menu mobile
  document.getElementById('mobileMenu').classList.toggle('open');
}

// Ferme le menu si on clique en dehors
document.addEventListener('click', function(e) {
  const menu      = document.getElementById('mobileMenu');
  const hamburger = document.querySelector('.hamburger');

  // Si le clic n'est ni dans le menu ni sur le hamburger → on ferme
  if (!menu.contains(e.target) && !hamburger.contains(e.target)) {
    menu.classList.remove('open');
  }
});


// ============================================================
// ANIMATION AU SCROLL — Apparition des éléments
// ============================================================

/**
 * IntersectionObserver : surveille quand un élément entre dans l'écran
 * Quand c'est le cas, on ajoute la classe "visible" pour déclencher l'animation CSS
 */
const observer = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry, index) {
    if (entry.isIntersecting) {
      // Délai progressif pour les éléments qui apparaissent ensemble
      setTimeout(function() {
        entry.target.classList.add('visible');
      }, index * 80);

      // On arrête d'observer cet élément (l'animation ne se rejoue pas)
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 }); // Se déclenche quand 10% de l'élément est visible

// On applique l'observation à tous les éléments avec la classe "reveal"
document.querySelectorAll('.reveal').forEach(function(el) {
  observer.observe(el);
});


// ============================================================
// FORMULAIRE DE CONTACT — Envoi vers Flask
// ============================================================

/**
 * Envoie les données du formulaire à la route Flask /contact
 * Utilise fetch() pour envoyer une requête HTTP POST en JSON
 */
function envoyerMessage() {

  // Récupération des valeurs des champs du formulaire
  const prenom  = document.getElementById('prenom').value.trim();
  const nom     = document.getElementById('nom').value.trim();
  const email   = document.getElementById('email').value.trim();
  const objet   = document.getElementById('objet').value;
  const message = document.getElementById('message').value.trim();

  // Vérification côté client (avant d'envoyer au serveur)
  if (!prenom || !email || !message) {
    alert('⚠️ Veuillez remplir les champs obligatoires : Prénom, Email et Message.');
    return; // On arrête ici si des champs sont vides
  }

  // Envoi de la requête POST vers Flask avec les données en JSON
  fetch('/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prenom, nom, email, objet, message })
  })
  .then(function(response) {
    // On lit la réponse JSON de Flask
    return response.json();
  })
  .then(function(data) {
    const msgDiv = document.getElementById('successMsg');

    if (data.success) {
      // ✅ Succès : on affiche le message de confirmation
      msgDiv.style.display = 'block';
      msgDiv.style.color   = '#2d6a4f';
      msgDiv.style.borderColor = '#2d6a4f';
      msgDiv.style.background  = 'rgba(45,106,79,0.1)';
      msgDiv.textContent = data.message;

      // On vide les champs du formulaire
      document.getElementById('prenom').value  = '';
      document.getElementById('nom').value     = '';
      document.getElementById('email').value   = '';
      document.getElementById('objet').value   = '';
      document.getElementById('message').value = '';

    } else {
      // ❌ Erreur serveur : on affiche le message d'erreur
      msgDiv.style.display = 'block';
      msgDiv.style.color   = '#dc2626';
      msgDiv.style.borderColor = '#dc2626';
      msgDiv.style.background  = 'rgba(220,38,38,0.1)';
      msgDiv.textContent = data.message;
    }
  })
  .catch(function(err) {
    // Erreur réseau (serveur Flask non démarré, etc.)
    console.error('Erreur réseau :', err);
    alert('❌ Erreur de connexion. Vérifiez que le serveur Flask est démarré.');
  });
}