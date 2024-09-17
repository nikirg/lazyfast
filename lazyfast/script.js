function throttle(func, wait = 1000) {
  let timeout = null;
  let lastArgs = null;

  return function (...args) {
    if (!timeout) {
      func.apply(this, args);
      timeout = setTimeout(() => {
        timeout = null;
        if (lastArgs) {
          func.apply(this, lastArgs);
          lastArgs = null;
        }
      }, wait);
    } else {
      lastArgs = args;
    }
  };
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
      indicatorElmContent.innerHTML = indicatorElmContent.dataset.htmxIndicatorContent;
    }
  }

  const extraVals = JSON.stringify({ __tid__: element.id, __evt__: event?.type });
  componentLoader.setAttribute('hx-vals', extraVals);
  htmx.trigger(componentLoader, componentLoader.id);
}

function preventFormSubmission(event) {
  event.preventDefault();
}

const throttledReloadComponent = throttle(reloadComponent);


function saveInputData() {
  const inputs = document.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    if (input.type !== 'hidden') {
      localStorage.setItem(input.name || input.id, input.value);
    }
  });
}

function restoreInputDataForElement(element) {
  const inputs = element.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    if (input.type !== 'hidden') {
      const savedValue = localStorage.getItem(input.name || input.id);
      if (savedValue) {
        input.value = savedValue;
        localStorage.removeItem(input.name || input.id);
      }
    }
  });
}


htmx.on('htmx:afterSettle', function (evt) {
  restoreInputDataForElement(evt.target);
});


window.onload = function () {
  let sse = document.body.dataset.sse;

  if (!sse) {
    return;
  }

  const lastEvent = localStorage.getItem("sse_last_event");

  if (lastEvent) {
    sse = `${sse}?last_event=${lastEvent}`;
  }

  const sseSource = new EventSource(sse);

  sseSource.onmessage = function (event) {
    const target = document.getElementById(event.data);
    localStorage.setItem("sse_last_event", event.data);
    if (target) {
      reloadComponent(target);
    }
  };

  sseSource.onerror = function (error) {
    saveInputData();
    document.location.reload();
  };
}
