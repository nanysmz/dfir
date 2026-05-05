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
    dropdown.style.maxHeight = "320px";
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

  function hideDropdown(dropdown) {
    dropdown.style.display = "none";
  }

  function renderEmpty(dropdown, label) {
    dropdown.innerHTML = "";
    const empty = document.createElement("div");
    empty.textContent = label || "Sin coincidencias";
    empty.style.padding = "8px 10px";
    empty.style.color = "#64748b";
    empty.style.fontSize = "0.92rem";
    dropdown.appendChild(empty);
    dropdown.style.display = "block";
  }

  function attachAutocomplete(input) {
    const url = input.dataset.mountedPathAutocompleteUrl;
    if (!url) {
      return;
    }

    const listId = input.id + "__mounted_paths";
    let datalist = document.getElementById(listId);
    if (!datalist) {
      datalist = document.createElement("datalist");
      datalist.id = listId;
      input.insertAdjacentElement("afterend", datalist);
    }
    input.setAttribute("list", listId);

    const dropdown = createDropdown(input);

    const fetchSuggestions = debounce(function () {
      const value = (input.value || "").trim();
      const query = encodeURIComponent(value);
      fetch(url + "?q=" + query, { credentials: "same-origin" })
        .then(function (response) {
          if (!response.ok) {
            return { results: [] };
          }
          return response.json();
        })
        .then(function (payload) {
          datalist.innerHTML = "";
          const results = Array.isArray(payload.results) ? payload.results : [];
          if (!results.length) {
            renderEmpty(dropdown, "Sin coincidencias");
            return;
          }

          dropdown.innerHTML = "";
          results.forEach(function (entry) {
            const option = document.createElement("option");
            option.value = entry.value;
            datalist.appendChild(option);

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
              input.value = entry.value;
              hideDropdown(dropdown);
            });
            dropdown.appendChild(item);
          });
          dropdown.style.display = "block";
        })
        .catch(function () {
          datalist.innerHTML = "";
          hideDropdown(dropdown);
        });
    }, 220);

    input.addEventListener("input", fetchSuggestions);
    input.addEventListener("focus", fetchSuggestions);
    input.addEventListener("click", fetchSuggestions);
    document.addEventListener("click", function (event) {
      if (!dropdown.parentNode.contains(event.target)) {
        hideDropdown(dropdown);
      }
    });
    fetchSuggestions();
  }

  function createBrowserHeader(state, onBack) {
    const header = document.createElement("div");
    header.style.position = "sticky";
    header.style.top = "0";
    header.style.background = "#f8fafc";
    header.style.borderBottom = "1px solid #e2e8f0";
    header.style.padding = "8px 10px";
    header.style.zIndex = "1";

    const title = document.createElement("div");
    title.textContent = state.currentLabel || "Raices montadas";
    title.style.fontWeight = "600";
    title.style.fontSize = "0.88rem";
    title.style.color = "#0f172a";
    header.appendChild(title);

    const subtitle = document.createElement("div");
    subtitle.textContent = state.selectedPath
      ? "Ruta seleccionada: " + state.selectedPath
      : "Explora carpetas o selecciona una ruta.";
    subtitle.style.fontSize = "0.8rem";
    subtitle.style.color = "#64748b";
    subtitle.style.marginTop = "2px";
    header.appendChild(subtitle);

    if (state.parentPath) {
      const back = document.createElement("button");
      back.type = "button";
      back.textContent = "Volver";
      back.style.marginTop = "8px";
      back.style.padding = "4px 8px";
      back.style.border = "1px solid #cbd5e1";
      back.style.borderRadius = "6px";
      back.style.background = "#fff";
      back.style.cursor = "pointer";
      back.addEventListener("click", function () {
        onBack(state.parentPath);
      });
      header.appendChild(back);
    }

    return header;
  }

  function createBrowserRow(entry, onNavigate, onSelect) {
    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.alignItems = "center";
    row.style.gap = "8px";
    row.style.padding = "8px 10px";
    row.style.borderBottom = "1px solid #f1f5f9";

    const label = document.createElement("div");
    label.style.flex = "1";
    label.style.minWidth = "0";
    label.style.fontSize = "0.92rem";
    label.style.color = "#0f172a";
    label.style.whiteSpace = "nowrap";
    label.style.overflow = "hidden";
    label.style.textOverflow = "ellipsis";
    label.textContent = entry.label || entry.value;
    row.appendChild(label);

    if (entry.is_directory) {
      const openButton = document.createElement("button");
      openButton.type = "button";
      openButton.textContent = "Abrir";
      openButton.style.padding = "4px 8px";
      openButton.style.border = "1px solid #cbd5e1";
      openButton.style.borderRadius = "6px";
      openButton.style.background = "#fff";
      openButton.style.cursor = "pointer";
      openButton.addEventListener("click", function () {
        onNavigate(entry.value);
      });
      row.appendChild(openButton);
    }

    const selectButton = document.createElement("button");
    selectButton.type = "button";
    selectButton.textContent = entry.is_directory ? "Usar carpeta" : "Seleccionar";
    selectButton.style.padding = "4px 8px";
    selectButton.style.border = "1px solid #7c3aed";
    selectButton.style.borderRadius = "6px";
    selectButton.style.background = "#faf5ff";
    selectButton.style.color = "#6d28d9";
    selectButton.style.cursor = "pointer";
    selectButton.addEventListener("click", function () {
      onSelect(entry.value);
    });
    row.appendChild(selectButton);

    return row;
  }

  function attachBrowser(input) {
    const url = input.dataset.mountedPathAutocompleteUrl;
    if (!url) {
      return;
    }

    const dropdown = createDropdown(input);
    const state = {
      currentPath: "",
      currentLabel: "Raices montadas",
      parentPath: "",
      selectedPath: (input.value || "").trim(),
    };

    function renderBrowser(results) {
      dropdown.innerHTML = "";
      dropdown.appendChild(
        createBrowserHeader(state, function (parentPath) {
          loadBrowser({ currentPath: parentPath, keepInputValue: true });
        })
      );

      if (!results.length) {
        const empty = document.createElement("div");
        empty.textContent = "Sin elementos en esta ubicacion";
        empty.style.padding = "8px 10px";
        empty.style.color = "#64748b";
        empty.style.fontSize = "0.92rem";
        dropdown.appendChild(empty);
        dropdown.style.display = "block";
        return;
      }

      results.forEach(function (entry) {
        dropdown.appendChild(
          createBrowserRow(
            entry,
            function (nextPath) {
              loadBrowser({ currentPath: nextPath, keepInputValue: true });
            },
            function (selectedValue) {
              state.selectedPath = selectedValue;
              input.value = selectedValue;
              hideDropdown(dropdown);
            }
          )
        );
      });
      dropdown.style.display = "block";
    }

    function buildQuery(params) {
      const search = new URLSearchParams();
      search.set("browser", "1");
      if (params.currentPath) {
        search.set("current_path", params.currentPath);
      }
      if (params.resolve) {
        search.set("resolve", params.resolve);
      }
      if (params.query) {
        search.set("q", params.query);
      }
      return search.toString();
    }

    function loadBrowser(params) {
      const query = buildQuery(params || {});
      fetch(url + "?" + query, { credentials: "same-origin" })
        .then(function (response) {
          if (!response.ok) {
            return { results: [] };
          }
          return response.json();
        })
        .then(function (payload) {
          state.currentPath = payload.current_path || "";
          state.currentLabel = payload.current_label || "Raices montadas";
          state.parentPath = payload.parent_path || "";
          state.selectedPath = payload.selected_path || state.selectedPath || "";
          if (!params || !params.keepInputValue) {
            if (!params.query && state.selectedPath) {
              input.value = state.selectedPath;
            }
          }
          renderBrowser(Array.isArray(payload.results) ? payload.results : []);
        })
        .catch(function () {
          hideDropdown(dropdown);
        });
    }

    const handleInput = debounce(function () {
      const value = (input.value || "").trim();
      if (!value) {
        state.selectedPath = "";
        loadBrowser({});
        return;
      }
      loadBrowser({
        currentPath: state.currentPath,
        query: value,
        keepInputValue: true,
      });
    }, 220);

    input.addEventListener("focus", function () {
      const value = (input.value || "").trim();
      if (value) {
        loadBrowser({ resolve: value });
        return;
      }
      loadBrowser({});
    });
    input.addEventListener("click", function () {
      const value = (input.value || "").trim();
      if (value && !dropdown.style.display) {
        loadBrowser({ resolve: value });
        return;
      }
      if (!value) {
        loadBrowser({});
      }
    });
    input.addEventListener("input", handleInput);
    document.addEventListener("click", function (event) {
      if (!dropdown.parentNode.contains(event.target)) {
        hideDropdown(dropdown);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const selector = "input[data-mounted-path-autocomplete-url]";
    document.querySelectorAll(selector).forEach(function (input) {
      if (input.dataset.mountedPathBrowser === "true") {
        attachBrowser(input);
        return;
      }
      attachAutocomplete(input);
    });
  });
})();
