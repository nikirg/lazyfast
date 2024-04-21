function reloadComponent(triggerElement) {
    const componentLoader = triggerElement.closest('.__componentLoader__');
    componentLoader.setAttribute('hx-vals', JSON.stringify({ "__tid__": triggerElement.id }));

    componentLoader.querySelectorAll('[data-htmx-indicator-class]').forEach((el) => {
        el.classList.add(el.dataset['htmxIndicatorClass']);
    })
    
    htmx.trigger(componentLoader, 'reload');
}

