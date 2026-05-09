const DEFAULT_PAGE_TITLE = "Пифагор";

function getRouteTitle(route) {
    return route.meta?.title || DEFAULT_PAGE_TITLE;
}

export function setupRouterGuards(router) {
    router.beforeEach(() => {
        return true;
    });

    router.afterEach((to) => {
        document.title = getRouteTitle(to);
    });
}