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

htmx.on('htmx:sseError', function (evt) { document.location.reload(); });

