export const adminRoutes = [
    {
        path: "/admin",
        redirect: {
            name: "admin.dashboard",
        },
    },
    {
        path: "/admin/dashboard",
        name: "admin.dashboard",
        component: () => import("../pages/admin/AdminDashboardPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Панель администратора  | Пифагор",
        },
    },
    {
        path: "/admin/users",
        name: "admin.users",
        component: () => import("../pages/admin/UsersPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Пользователи  | Пифагор",
        },
    },
    {
        path: "/admin/organizations",
        name: "admin.organizations",
        component: () => import("../pages/admin/OrganizationsPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Организации  | Пифагор",
        },
    },
    {
        path: "/admin/groups",
        name: "admin.groups",
        component: () => import("../pages/admin/GroupsPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Группы  | Пифагор",
        },
    },
    {
        path: "/admin/education",
        name: "admin.education",
        component: () => import("../pages/admin/EducationPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Учебная структура  | Пифагор",
        },
    },
    {
        path: "/admin/courses",
        name: "admin.courses",
        component: () => import("../pages/admin/CoursesPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Курсы  | Пифагор",
        },
    },
    {
        path: "/admin/schedule",
        name: "admin.schedule",
        component: () => import("../pages/admin/SchedulePage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Расписание  | Пифагор",
        },
    },
    {
        path: "/admin/feedback",
        name: "admin.feedback",
        component: () => import("../pages/admin/FeedbackRequestsPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["admin"],
            title: "Обращения  | Пифагор",
        },
    },
];
