export const errorRoutes = [
    {
        path: "/403",
        name: "errors.forbidden",
        component: () => import("../pages/errors/ForbiddenPage.vue"),
        meta: {
            isPublic: true,
            title: "Доступ запрещён — Пифагор",
        },
    },
    {
        path: "/500",
        name: "errors.server",
        component: () => import("../pages/errors/ServerErrorPage.vue"),
        meta: {
            isPublic: true,
            title: "Ошибка сервера — Пифагор",
        },
    },
    {
        path: "/:pathMatch(.*)*",
        name: "errors.not-found",
        component: () => import("../pages/errors/NotFoundPage.vue"),
        meta: {
            isPublic: true,
            title: "Страница не найдена — Пифагор",
        },
    },
];