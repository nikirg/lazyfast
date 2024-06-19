_TRHOTTLE = """
function throttle(func, wait=1000) {
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
"""

_RELOAD_COMPONENT = """
function reloadComponent(element) {
    const componentLoader = element.closest('.__componentLoader__');
    const cssSelector = '[data-htmx-indicator-class], [data-htmx-indicator-content]';
        
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

    const tid = document.createElement("input");
    tid.type = "hidden";
    tid.name = "__tid__";
    tid.value = element.id;
    tid.style.display = 'none';
    tid.style.position = 'absolute';
    tid.style.zIndex = '-1';
    componentLoader.appendChild(tid)
    
    //componentLoader.dataset.htmxPost = componentLoader.dataset.htmxPost + '?tid=' + element.id;
    //componentLoader.dataset.htmxHeaders = `{'X-Trigger-Element-Id': ${element.id}}`;
    
    htmx.trigger(componentLoader, componentLoader.id);
}

const throttledReloadComponent = throttle(reloadComponent);
"""

SCRIPT = """%s%s
htmx.on('htmx:sseError', function(evt){ document.location.reload(); });

function preventFormSubmission(event) {
    event.preventDefault();
}
""" % (
    _TRHOTTLE,
    _RELOAD_COMPONENT,
)
