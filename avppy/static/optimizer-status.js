(() => {
  const container = document.querySelector("[data-optimizer-status]");
  if (!container) return;

  const title = container.querySelector("[data-optimizer-title]");
  const detail = container.querySelector("[data-optimizer-detail]");

  function render(status) {
    const pending = Array.isArray(status.pending_modes) && status.pending_modes.length > 0;
    let titleText = "";
    let detailText = "";

    if (status.processing) {
      const phase = status.phase || "Traitement en cours";
      titleText = status.current_file ? `${phase} : ${status.current_file}` : phase;
      if (status.playback_paused) {
        detailText = "Lecture suspendue automatiquement. Elle reprendra à la fin du traitement.";
      } else if (status.maintenance_active) {
        detailText = "La lecture était déjà inactive avant le traitement.";
      }
    } else if (pending) {
      titleText = status.sync_active
        ? "Traitement en attente de la fin de la synchronisation."
        : "Traitement en attente de démarrage.";
    } else if (status.last_message) {
      titleText = status.last_message;
    }

    container.hidden = !titleText;
    title.textContent = titleText;
    detail.textContent = detailText;
    detail.hidden = !detailText;
  }

  async function refresh() {
    try {
      const response = await fetch("/health", { cache: "no-store" });
      if (!response.ok) return;
      const payload = await response.json();
      render(payload.optimization || {});
    } catch (_) {
      // Conserve le dernier état connu si le Raspberry Pi est momentanément indisponible.
    }
  }

  refresh();
  window.setInterval(refresh, 1500);
})();
