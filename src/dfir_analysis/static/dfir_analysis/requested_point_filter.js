(function () {
  function buildOption(value, label, selected) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    if (selected) {
      option.selected = true;
    }
    return option;
  }

  function renderOptions(select, points, selectedValue) {
    select.innerHTML = "";
    select.appendChild(buildOption("", "Select value", !selectedValue));

    points.forEach(function (point) {
      const isSelected = String(point.id) === String(selectedValue || "");
      select.appendChild(buildOption(String(point.id), point.label, isSelected));
    });
  }

  function attachRequestedPointFilter() {
    const caseSelect = document.getElementById("id_pericia_case");
    const pointSelect = document.getElementById("id_requested_point");
    if (!caseSelect || !pointSelect) {
      return;
    }

    const url = pointSelect.dataset.requestedPointFilterUrl;
    if (!url) {
      return;
    }

    function refreshOptions() {
      const caseId = (caseSelect.value || "").trim();
      const selectedValue = pointSelect.value;
      if (!caseId) {
        renderOptions(pointSelect, [], "");
        return;
      }

      fetch(url + "?case_id=" + encodeURIComponent(caseId), {
        credentials: "same-origin",
      })
        .then(function (response) {
          if (!response.ok) {
            return { results: [] };
          }
          return response.json();
        })
        .then(function (payload) {
          const results = Array.isArray(payload.results) ? payload.results : [];
          renderOptions(pointSelect, results, selectedValue);
        })
        .catch(function () {
          renderOptions(pointSelect, [], "");
        });
    }

    let previousCaseId = (caseSelect.value || "").trim();

    function refreshIfChanged() {
      const currentCaseId = (caseSelect.value || "").trim();
      if (currentCaseId === previousCaseId) {
        return;
      }
      previousCaseId = currentCaseId;
      refreshOptions();
    }

    caseSelect.addEventListener("change", refreshOptions);
    caseSelect.addEventListener("input", refreshOptions);
    caseSelect.addEventListener("blur", refreshIfChanged);
    caseSelect.addEventListener("click", refreshIfChanged);
    caseSelect.addEventListener("keyup", refreshIfChanged);

    const observer = new MutationObserver(refreshIfChanged);
    observer.observe(caseSelect, {
      attributes: true,
      attributeFilter: ["value"],
      childList: true,
      subtree: true,
    });

    window.setInterval(refreshIfChanged, 250);
    refreshOptions();
  }

  document.addEventListener("DOMContentLoaded", attachRequestedPointFilter);
})();
