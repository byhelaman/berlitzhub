// Optimización: Eliminado location.reload() innecesario
// El back/forward cache del navegador es beneficioso y no requiere recarga
// Si necesitas refrescar datos específicos, hazlo de forma selectiva
window.addEventListener("pageshow", function (event) {
  // Solo refrescar si es necesario (por ejemplo, si hay datos que pueden haber cambiado)
  // Por ahora, confiamos en el cache del navegador para mejor rendimiento
  if (event.persisted) {
    // Opcional: puedes refrescar datos específicos aquí si es necesario
    // Por ejemplo: actualizar notificaciones, estado de sesión, etc.
  }
});
