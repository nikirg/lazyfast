const __PAGE_KEY__ = window.location.pathname;

function __storageKey__(name) {
  return __PAGE_KEY__ + ':' + name;
}

function reloadComponent(element, event) {
  const componentLoader = element.closest('.__componentLoader__');
  const indicatorElmClass = element.closest('[data-htmx-indicator-class]');
  const indicatorElmContent = element.closest('[data-htmx-indicator-content]');

  if (indicatorElmClass) {
    if (indicatorElmClass.dataset.htmxIndicatorClass) {
      indicatorElmClass.classList.add(indicatorElmClass.dataset.htmxIndicatorClass);
    }
  }

  if (indicatorElmContent) {
    if (indicatorElmContent.dataset.htmxIndicatorContent) {
      // Use textContent to avoid XSS — indicator content is treated as plain text
      indicatorElmContent.textContent = indicatorElmContent.dataset.htmxIndicatorContent;
    }
  }

  const extraVals = JSON.stringify({ __tid__: element.id, __evt__: event?.type });
  componentLoader.setAttribute('hx-vals', extraVals);
  htmx.trigger(componentLoader, componentLoader.id);
}

function preventFormSubmission(event) {
  event.preventDefault();
}

function saveInputData() {
  const inputs = document.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    if (input.type !== 'hidden') {
      localStorage.setItem(__storageKey__(input.name || input.id), input.value);
    }
  });
}

function restoreInputDataForElement(element) {
  const inputs = element.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    if (input.type !== 'hidden') {
      const key = __storageKey__(input.name || input.id);
      const savedValue = localStorage.getItem(key);
      if (savedValue) {
        input.value = savedValue;
        localStorage.removeItem(key);
      }
    }
  });
}

let _focusedId = null, _focusedName = null, _focusCursor = null;

htmx.on('htmx:beforeSwap', function (_evt) {
  const el = document.activeElement;
  if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA')) {
    _focusedId = el.id || null;
    _focusedName = el.name || null;
    _focusCursor = (el.selectionEnd != null) ? el.selectionEnd : null;
  } else {
    _focusedId = null;
    _focusedName = null;
    _focusCursor = null;
  }
});

htmx.on('htmx:afterSettle', function (evt) {
  restoreInputDataForElement(evt.target);

  if (_focusedId || _focusedName) {
    const selector = _focusedId
      ? `#${CSS.escape(_focusedId)}`
      : `[name="${CSS.escape(_focusedName)}"]`;
    const el = evt.target.querySelector(selector) || document.querySelector(selector);
    if (el) {
      el.focus();
      if (_focusCursor != null && el.setSelectionRange) {
        try { el.setSelectionRange(_focusCursor, _focusCursor); } catch (_) {}
      }
    }
    _focusedId = null;
    _focusedName = null;
    _focusCursor = null;
  }
});

htmx.on('htmx:responseError', function (evt) {
  if (evt.detail.xhr.status === 403) {
    document.location.reload();
  }
});

window.onload = function () {
  let sse = document.body.dataset.sse;

  if (!sse) {
    return;
  }

  const lastEventKey = __storageKey__('sse_last_event');
  const lastEvent = localStorage.getItem(lastEventKey);

  if (lastEvent) {
    sse = `${sse}?last_event=${lastEvent}`;
  }

  const sseSource = new EventSource(sse);

  sseSource.onmessage = function (event) {
    // Server sends __reload__ when the event buffer has rolled over
    if (event.data === '__reload__') {
      localStorage.removeItem(lastEventKey);
      document.location.reload();
      return;
    }

    const target = document.getElementById(event.data);
    localStorage.setItem(lastEventKey, event.data);
    if (target) {
      reloadComponent(target);
    }
  };

  sseSource.onerror = function (error) {
    saveInputData();
    document.location.reload();
  };
}
