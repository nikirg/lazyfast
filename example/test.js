function reloadComponent(triggerElement) {
    const componentLoader = triggerElement.closest('.__componentLoader__');
    componentLoader.setAttribute('hx-vals', JSON.stringify({ "__tid__": triggerElement.id }));
    htmx.trigger(componentLoader, 'reload');
}

