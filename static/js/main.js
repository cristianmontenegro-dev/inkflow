// Esperar a que el DOM cargue
document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');
  
  // Revisar si el usuario ya tenía un tema guardado
  const currentTheme = localStorage.getItem('theme') || 'dark';
  
  // Aplicar el tema guardado
  document.documentElement.setAttribute('data-theme', currentTheme);
  themeIcon.textContent = currentTheme === 'dark' ? '🌙' : '☀️';

  // Evento de clic en el botón
  themeToggle.addEventListener('click', () => {
    let theme = document.documentElement.getAttribute('data-theme');
    
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('theme', 'light');
      themeIcon.textContent = '☀️';
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
      themeIcon.textContent = '🌙';
    }
  });
});