/**
 * Script para duplicación de elementos de evidencia en el inline
 * Permite crear copias de dispositivos con un click
 */
(function() {
  "use strict";

  function findFormsetPrefix() {
    // Busca un input con name que contenga el prefijo del formset (ej: dfir_pericia-evidenceitem_set-TOTAL_FORMS)
    const totalFormsInput = document.querySelector('[name*="TOTAL_FORMS"]');
    if (!totalFormsInput) return null;
    
    const match = totalFormsInput.name.match(/^(.+?)-TOTAL_FORMS$/);
    return match ? match[1] : null;
  }

  function getFormIndex(element) {
    // Extrae el índice de un formulario basado en su ID o atributos de nombre
    const id = element.id || '';
    const name = element.name || '';
    
    const idMatch = id.match(/-(\d+)-/);
    const nameMatch = name.match(/-(\d+)-/);
    
    return idMatch ? parseInt(idMatch[1]) : (nameMatch ? parseInt(nameMatch[1]) : -1);
  }

  function getLatestFormRow(prefix) {
    // Encuentra todas las filas del formset
    const rows = document.querySelectorAll(`[data-formset-inline-item]`);
    if (rows.length === 0) {
      // Fallback: busca por estructura de IDs
      const allForms = document.querySelectorAll(`[id*="${prefix}-"]`);
      if (allForms.length === 0) return null;
      
      let maxIndex = -1;
      let latestForm = null;
      
      allForms.forEach(form => {
        const idx = getFormIndex(form);
        if (idx > maxIndex) {
          maxIndex = idx;
          latestForm = form.closest('[data-formset-inline-item]') || form.closest('div[data-formset-inline-item]');
        }
      });
      
      return latestForm;
    }
    
    return rows[rows.length - 1];
  }

  function getNextDeviceLabelFromInline(prefix) {
    const pattern = /^Dispositivo\s+(\d+)$/i;
    let maxNumber = 0;

    document
      .querySelectorAll(`[name^="${prefix}-"][name$="-label"]`)
      .forEach((input) => {
        const value = String(input.value || '').trim();
        const match = value.match(pattern);
        if (match) {
          const n = parseInt(match[1], 10);
          if (!Number.isNaN(n)) {
            maxNumber = Math.max(maxNumber, n);
          }
        }
      });

    return `Dispositivo ${maxNumber + 1}`;
  }

  function duplicateLatestForm() {
    const prefix = findFormsetPrefix();
    if (!prefix) {
      console.warn('No se encontró el prefijo del formset de EvidenceItem');
      return;
    }

    const latestRow = getLatestFormRow(prefix);
    if (!latestRow) {
      console.warn('No se encontró la fila del formulario más reciente');
      return;
    }

    const totalFormsInput = document.querySelector(`[name="${prefix}-TOTAL_FORMS"]`);
    const currentCount = parseInt(totalFormsInput.value || '0');
    const newIndex = currentCount;

    // Clona la fila
    const clone = latestRow.cloneNode(true);

    // Actualiza todos los índices de campos en el clon
    clone.querySelectorAll('[name], [id], [for]').forEach(el => {
      const name = el.getAttribute('name');
      if (name) {
        const newName = name.replace(new RegExp(`${prefix}-(\\d+)-`), `${prefix}-${newIndex}-`);
        el.setAttribute('name', newName);
      }

      const id = el.getAttribute('id');
      if (id) {
        const newId = id.replace(new RegExp(`${prefix}_(\\d+)_`), `${prefix}_${newIndex}_`);
        el.setAttribute('id', newId);
      }

      const forAttr = el.getAttribute('for');
      if (forAttr) {
        const newFor = forAttr.replace(new RegExp(`${prefix}_(\\d+)_`), `${prefix}_${newIndex}_`);
        el.setAttribute('for', newFor);
      }
    });

    const nextLabel = getNextDeviceLabelFromInline(prefix);

    // Limpia ciertos campos
    clone.querySelectorAll('input[type="text"], input[type="number"], textarea, select').forEach(field => {
      const fieldName = field.getAttribute('name') || '';

      // Limpia el ID del formulario (para que sea un nuevo objeto)
      if (fieldName.includes('-id')) {
        field.value = '';
      }

      // Desmarca DELETE si existe
      if (fieldName.includes('-DELETE')) {
        field.checked = false;
      }

      // Asigna etiqueta secuencial del dispositivo
      if (fieldName.includes('-label')) {
        field.value = nextLabel;
      }
    });

    // Inserta el clon después de la última fila
    const container = latestRow.parentElement;
    container.insertBefore(clone, latestRow.nextElementSibling);

    // Actualiza el contador total de formularios
    totalFormsInput.value = newIndex + 1;

    // Scroll al nuevo formulario
    clone.scrollIntoView({ behavior: 'smooth', block: 'center' });

    console.log(`✓ Dispositivo duplicado: nueva fila ${newIndex}`);
  }

  function addDuplicateButton() {
    const prefix = findFormsetPrefix();
    if (!prefix || !prefix.includes('evidenceitem')) return;

    // Busca el botón de agregar del inline
    const addButtons = document.querySelectorAll('button');
    let addButton = null;

    for (let btn of addButtons) {
      const text = btn.textContent.toLowerCase();
      if (text.includes('agregar') || text.includes('add') || text.includes('+')) {
        // Verifica que esté cerca del inline de evidencia
        const parent = btn.closest('[data-inline-name]');
        if (parent && parent.getAttribute('data-inline-name').includes('evidence')) {
          addButton = btn;
          break;
        }
      }
    }

    if (addButton && !document.querySelector('[data-duplicate-evidence-btn]')) {
      const dupButton = document.createElement('button');
      dupButton.type = 'button';
      dupButton.setAttribute('data-duplicate-evidence-btn', 'true');
      dupButton.className = addButton.className;
      dupButton.innerHTML = '📋 Duplicar último dispositivo';
      dupButton.style.marginLeft = '8px';

      dupButton.addEventListener('click', (e) => {
        e.preventDefault();
        duplicateLatestForm();
      });

      addButton.parentElement.insertBefore(dupButton, addButton.nextElementSibling);
      console.log('✓ Botón duplicar agregado al inline de Elementos de evidencia');
    }
  }

  // Inicia cuando el DOM esté listo
  function init() {
    setTimeout(addDuplicateButton, 500); // Pequeño delay para que Unfold cargue todo
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
