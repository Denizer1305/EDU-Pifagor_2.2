export const parentRoutes = [
    {
        path: "/parent",
        redirect: {
            name: "parent.dashboard",
        },
    },
    {
        path: "/parent/dashboard",
        name: "parent.dashboard",
        component: () => import("../pages/parent/ParentDashboardPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["parent"],
            title: "Кабинет родителя — Пифагор",
        },
    },
    {
        path: "/parent/children",
        name: "parent.children",
        component: () => import("../pages/parent/ParentChildrenPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["parent"],
            title: "Дети — Пифагор",
        },
    },
    {
        path: "/parent/journal",
        name: "parent.journal",
        component: () => import("../pages/parent/ParentJournalPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["parent"],
            title: "Журнал — Пифагор",
        },
    },
    {
        path: "/parent/attendance",
        name: "parent.attendance",
        component: () => import("../pages/parent/ParentAttendancePage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["parent"],
            title: "Посещаемость — Пифагор",
        },
    },
    {
        path: "/parent/schedule",
        name: "parent.schedule",
        component: () => import("../pages/parent/ParentSchedulePage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["parent"],
            title: "Расписание — Пифагор",
        },
    },
];