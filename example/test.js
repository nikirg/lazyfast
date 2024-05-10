function reloadComponents(ids) {
    const elements = ids.map(id => document.getElementById(id));
    elements.forEach((element) => { reloadComponent(element); })
}

function reloadComponent(element) {
    const componentLoader = element.closest('.__componentLoader__');
    componentLoader.setAttribute('hx-vals', JSON.stringify({ "__tid__": element.id }));
    componentLoader.querySelectorAll('[data-htmx-indicator-class]').forEach((el) => {
        el.classList.add(el.dataset['htmxIndicatorClass']);
    })
    htmx.trigger(componentLoader, 'reload');

}