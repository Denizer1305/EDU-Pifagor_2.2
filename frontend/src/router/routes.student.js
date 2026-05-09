export const studentRoutes = [
    {
        path: "/student",
        redirect: {
            name: "student.dashboard",
        },
    },
    {
        path: "/student/dashboard",
        name: "student.dashboard",
        component: () => import("../pages/student/StudentDashboardPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Кабинет обучающегося — Пифагор",
        },
    },
    {
        path: "/student/courses",
        name: "student.courses",
        component: () => import("../pages/student/StudentCoursesPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Мои курсы — Пифагор",
        },
    },
    {
        path: "/student/courses/:id",
        name: "student.course-detail",
        component: () => import("../pages/student/StudentCourseDetailPage.vue"),
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Курс — Пифагор",
        },
    },
    {
        path: "/student/assignments",
        name: "student.assignments",
        component: () => import("../pages/student/StudentAssignmentsPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Задания — Пифагор",
        },
    },
    {
        path: "/student/assignments/:id",
        name: "student.assignment-detail",
        component: () => import("../pages/student/StudentAssignmentDetailPage.vue"),
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Задание — Пифагор",
        },
    },
    {
        path: "/student/submissions/:id",
        name: "student.submission",
        component: () => import("../pages/student/StudentSubmissionPage.vue"),
        props: true,
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Сдача работы — Пифагор",
        },
    },
    {
        path: "/student/journal",
        name: "student.journal",
        component: () => import("../pages/student/StudentJournalPage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Журнал — Пифагор",
        },
    },
    {
        path: "/student/schedule",
        name: "student.schedule",
        component: () => import("../pages/student/StudentSchedulePage.vue"),
        meta: {
            requiresAuth: true,
            roles: ["student"],
            title: "Расписание — Пифагор",
        },
    },
];
