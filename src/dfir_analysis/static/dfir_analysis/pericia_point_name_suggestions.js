(function () {
  function debounce(fn, delay) {
    let timeoutId = null;
    return function debounced() {
      const args = arguments;
      const context = this;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(function () {
        fn.apply(context, args);
      }, delay);
    };
  }

  function createDropdown(input) {
    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const dropdown = document.createElement("div");
    dropdown.style.position = "absolute";
    dropdown.style.top = "100%";
    dropdown.style.left = "0";
    dropdown.style.right = "0";
    dropdown.style.maxHeight = "280px";
    dropdown.style.overflowY = "auto";
    dropdown.style.background = "#fff";
    dropdown.style.border = "1px solid #d1d5db";
    dropdown.style.borderRadius = "8px";
    dropdown.style.marginTop = "4px";
    dropdown.style.boxShadow = "0 8px 18px rgba(15, 23, 42, 0.1)";
    dropdown.style.zIndex = "1000";
    dropdown.style.display = "none";

    wrapper.appendChild(dropdown);
    return dropdown;
  }

  function renderDropdown(dropdown, values, onSelect) {
    dropdown.innerHTML = "";
    if (!values.length) {
      dropdown.style.display = "none";
      return;
    }

    values.forEach(function (entry) {
      const item = document.createElement("button");
      item.type = "button";
      item.textContent = entry.label || entry.value;
      item.style.display = "block";
      item.style.width = "100%";
      item.style.padding = "8px 10px";
      item.style.textAlign = "left";
      item.style.background = "transparent";
      item.style.border = "none";
      item.style.cursor = "pointer";
      item.style.fontSize = "0.92rem";
      item.style.whiteSpace = "nowrap";
      item.style.overflow = "hidden";
      item.style.textOverflow = "ellipsis";
      item.addEventListener("mouseenter", function () {
        item.style.background = "#f8fafc";
      });
      item.addEventListener("mouseleave", function () {
        item.style.background = "transparent";
      });
      item.addEventListener("click", function () {
        onSelect(entry.value);
      });
      dropdown.appendChild(item);
    });
    dropdown.style.display = "block";
  }

  function attachNameSuggestions(input) {
    const url = input.dataset.periciaPointNameSuggestionsUrl;
    const caseSelect = document.getElementById("id_pericia_case");
    if (!url || !caseSelect) {
      return;
    }

    const dropdown = createDropdown(input);

    function hideDropdown() {
      dropdown.style.display = "none";
    }

    const fetchSuggestions = debounce(function () {
      const caseId = (caseSelect.value || input.dataset.selectedCaseId || "").trim();
      if (!caseId) {
        hideDropdown();
        return;
      }
      const query = encodeURIComponent((input.value || "").trim());
      fetch(url + "?case_id=" + encodeURIComponent(caseId) + "&q=" + query, {
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
          renderDropdown(dropdown, results, function (selectedValue) {
            input.value = selectedValue;
            hideDropdown();
          });
        })
        .catch(function () {
          hideDropdown();
        });
    }, 180);

    input.addEventListener("input", fetchSuggestions);
    input.addEventListener("focus", fetchSuggestions);
    input.addEventListener("click", fetchSuggestions);
    caseSelect.addEventListener("change", function () {
      input.dataset.selectedCaseId = caseSelect.value || "";
      fetchSuggestions();
    });
    document.addEventListener("click", function (event) {
      if (!dropdown.parentNode.contains(event.target)) {
        hideDropdown();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document
      .querySelectorAll("input[data-pericia-point-name-suggestions-url]")
      .forEach(attachNameSuggestions);
  });
})();
