(function () {
  const TAB_STORAGE_KEY = "dfir_case_active_tab_label";
  const KNOWN_CASE_TABS = new Set([
    "general",
    "puntos solicitados",
    "elementos de evidencia",
    "secciones del informe",
  ]);

  function normalizedText(value) {
    return String(value || "")
      .trim()
      .replace(/\s+/g, " ")
      .toLowerCase();
  }

  function isKnownCaseTab(element) {
    const label = normalizedText(element && element.textContent);
    return KNOWN_CASE_TABS.has(label);
  }

  function isActiveTab(element) {
    if (!element) {
      return false;
    }
    const className = String(element.className || "").toLowerCase();
    if (/(^|\s)(active|selected|current)(\s|$)/.test(className)) {
      return true;
    }
    if (String(element.getAttribute("aria-selected") || "").toLowerCase() === "true") {
      return true;
    }
    return false;
  }

  function getActiveTabLabel() {
    const active = getTabCandidates().find(isActiveTab);
    if (!active) {
      return "";
    }
    return String(active.textContent || "").trim();
  }

  function getTabCandidates() {
    const candidates = Array.from(
      document.querySelectorAll(
        "[role='tab'], .tabs button, .tabs a, .tab button, .tab a, button, a"
      )
    );
    return candidates.filter(isKnownCaseTab);
  }

  function activateTabByLabel(label) {
    const normalizedLabel = normalizedText(label);
    if (!normalizedLabel) {
      return;
    }

    const candidate = getTabCandidates().find(function (tab) {
      return normalizedText(tab.textContent) === normalizedLabel;
    });
    if (candidate) {
      candidate.click();
    }
  }

  function attachTabPersistence() {
    getTabCandidates().forEach(function (tab) {
      tab.addEventListener("click", function () {
        const label = String(tab.textContent || "").trim();
        if (label) {
          sessionStorage.setItem(TAB_STORAGE_KEY, label);
        }
      });
    });

    const forms = document.querySelectorAll("form");
    forms.forEach(function (form) {
      if (!form.querySelector("input[name='_active_tab_label']")) {
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "_active_tab_label";
        form.appendChild(hidden);
      }

      form.addEventListener("submit", function () {
        const activeLabel = getActiveTabLabel() || sessionStorage.getItem(TAB_STORAGE_KEY) || "";
        const hidden = form.querySelector("input[name='_active_tab_label']");
        if (hidden) {
          hidden.value = activeLabel;
        }
        if (activeLabel) {
          sessionStorage.setItem(TAB_STORAGE_KEY, activeLabel);
        }
      });
    });

    const params = new URLSearchParams(window.location.search);
    const requestedTab = params.get("_active_tab");
    const rememberedTab = sessionStorage.getItem(TAB_STORAGE_KEY);
    const targetTab = requestedTab || rememberedTab;
    if (targetTab) {
      window.setTimeout(function () {
        activateTabByLabel(targetTab);
      }, 10);
    }
  }

  function isInlineRow(node) {
    if (!(node instanceof HTMLElement)) {
      return false;
    }
    if (!node.classList.contains("inline-related")) {
      return false;
    }
    return !node.classList.contains("empty-form") && !node.id.endsWith("-empty");
  }

  function getInlineRows(group) {
    return Array.from(group.querySelectorAll(".inline-related")).filter(isInlineRow);
  }

  function setCollapsed(row, collapsed) {
    const details = row.querySelector("details");
    if (details) {
      details.open = !collapsed;
      return;
    }

    // Fallback for non-details collapse implementations.
    row.classList.toggle("collapsed", collapsed);
    row.querySelectorAll("fieldset").forEach(function (fieldset) {
      fieldset.classList.toggle("collapsed", collapsed);
    });
  }

  function collapseAllExcept(group, rowToKeepOpen) {
    const rows = getInlineRows(group);
    rows.forEach(function (row) {
      const shouldCollapse = row !== rowToKeepOpen;
      setCollapsed(row, shouldCollapse);
    });
  }

  function getNewlyAddedRow(group) {
    const rows = getInlineRows(group);
    return rows.length ? rows[rows.length - 1] : null;
  }

  function attachGroupBehavior(group) {
    const addButton = group.querySelector(
      ".add-row a, .add-row button, [data-inline-formset-add]"
    );

    if (addButton) {
      addButton.addEventListener("click", function () {
        window.setTimeout(function () {
          const newRow = getNewlyAddedRow(group);
          if (newRow) {
            collapseAllExcept(group, newRow);
          }
        }, 60);
      });
    }

    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (!isInlineRow(node)) {
            return;
          }
          collapseAllExcept(group, node);
        });
      });
    });

    observer.observe(group, { childList: true, subtree: true });
  }

  document.addEventListener("DOMContentLoaded", function () {
    attachTabPersistence();
    document
      .querySelectorAll(".inline-group, [data-inline-formset]")
      .forEach(attachGroupBehavior);
  });
})();
