export const publicRoutes = [
    {
        path: "/",
        component: () => import("../layouts/PublicLayout.vue"),
        meta: {
            isPublic: true,
        },
        children: [
            {
                path: "",
                name: "public.home",
                component: () => import("../pages/public/HomePage.vue"),
                meta: {
                    isPublic: true,
                    title: "Главная страница | Пифагор",
                },
            },
            {
                path: "about",
                name: "public.about",
                component: () => import("../pages/public/AboutPage.vue"),
                meta: {
                    isPublic: true,
                    title: "О платформе | Пифагор",
                },
            },
            {
                path: "teachers",
                name: "public.teachers",
                component: () => import("../pages/public/TeachersPage.vue"),
                meta: {
                    isPublic: true,
                    title: "Преподаватели | Пифагор",
                },
            },
            {
                path: "contacts",
                name: "public.contacts",
                component: () => import("../pages/public/ContactsPage.vue"),
                meta: {
                    isPublic: true,
                    title: "Контакты | Пифагор",
                },
            },
            {
                path: "feedback",
                name: "public.feedback",
                component: () => import("../pages/public/FeedbackPage.vue"),
                meta: {
                    isPublic: true,
                    title: "Обратная связь | Пифагор",
                },
            },
        ],
    },
];
