export const teacherRoutes = [
    {
        path: "/teacher",
        redirect: {
            name: "teacher.dashboard",
        },
    },
    {
        path: "/teacher/dashboard",
        name: "teacher.dashboard",
        component: () => import("../pages/teacher/TeacherDashboardPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Кабинет преподавателя — Пифагор",
        },
    },
    {
        path: "/teacher/courses",
        name: "teacher.courses",
        component: () => import("../pages/teacher/TeacherCoursesPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Мои курсы — Пифагор",
        },
    },
    {
        path: "/teacher/courses/:id",
        name: "teacher.course-detail",
        component: () => import("../pages/teacher/TeacherCourseDetailPage.vue"),
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Курс — Пифагор",
        },
    },
    {
        path: "/teacher/courses/:id/constructor",
        name: "teacher.course-constructor",
        component: () => import("../pages/teacher/TeacherCourseConstructorPage.vue"),
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Конструктор курса — Пифагор",
        },
    },
    {
        path: "/teacher/assignments",
        name: "teacher.assignments",
        component: () => import("../pages/teacher/TeacherAssignmentsPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Задания — Пифагор",
        },
    },
    {
        path: "/teacher/assignments/:id",
        name: "teacher.assignment-detail",
        component: () => import("../pages/teacher/TeacherAssignmentDetailPage.vue"),
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Задание — Пифагор",
        },
    },
    {
        path: "/teacher/submissions",
        name: "teacher.submissions",
        component: () => import("../pages/teacher/TeacherSubmissionsPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Сданные работы — Пифагор",
        },
    },
    {
        path: "/teacher/journal",
        name: "teacher.journal",
        component: () => import("../pages/teacher/TeacherJournalPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Журнал — Пифагор",
        },
    },
    {
        path: "/teacher/schedule",
        name: "teacher.schedule",
        component: () => import("../pages/teacher/TeacherSchedulePage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["teacher"],
            title: "Расписание — Пифагор",
        },
    },
];