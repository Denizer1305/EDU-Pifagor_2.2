export const authRoutes = [
    {
        path: "/auth",
        component: () => import("../layouts/AuthLayout.vue"),
        meta: {
            isPublic: true,
        },
        children: [
            {
                path: "login",
                name: "auth.login",
                component: () => import("../pages/auth/LoginPage.vue"),
                meta: {
                    title: "Вход в личный кабинет  | Пифагор",
                },
            },
            {
                path: "register",
                name: "auth.register",
                component: () => import("../pages/auth/RegisterPage.vue"),
                meta: {
                    title: "Регистрация на платформе | Пифагор",
                },
            },
            {
                path: "forgot-password",
                name: "auth.forgot-password",
                component: () => import("../pages/auth/ForgotPasswordPage.vue"),
                meta: {
                    title: "Восстановление пароля  | Пифагор",
                },
            },
            {
                path: "password-reset",
                name: "auth.password-reset",
                component: () => import("../pages/auth/PasswordResetPage.vue"),
                meta: {
                    title: "Сброс пароля  | Пифагор",
                },
            },
            {
                path: "email-verify",
                name: "auth.email-verify",
                component: () => import("../pages/auth/EmailVerifyPage.vue"),
                meta: {
                    title: "Подтверждение почты  | Пифагор",
                },
            },
            {
                path: "teacher-organization",
                name: "auth.teacher-organization",
                component: () => import("../pages/auth/TeacherOrganizationPage.vue"),
                meta: {
                    title: "Код организации  | Пифагор",
                },
            },
            {
                path: "logout",
                name: "auth.logout",
                component: () => import("../pages/auth/LogoutPage.vue"),
                meta: {
                    title: "Выход из аккаунта  | Пифагор",
                },
            },
            {
                path: "check-email",
                name: "auth.check-email",
                component: () => import("../pages/auth/CheckEmailPage.vue"),
                meta: {
                    title: "Проверьте почту  | Пифагор",
                },
            },
            {
                path: "email-verified",
                name: "auth.email-verified",
                component: () => import("../pages/auth/EmailVerifiedPage.vue"),
                meta: {
                    title: "Почта подтверждена  | Пифагор",
                },
            },
            {
                path: "teacher-pending",
                name: "auth.teacher-pending",
                component: () => import("../pages/auth/TeacherPendingPage.vue"),
                meta: {
                    title: "Заявка преподавателя  | Пифагор",
                },
            },
            {
                path: "link-expired",
                name: "auth.link-expired",
                component: () => import("../pages/auth/LinkExpiredPage.vue"),
                meta: {
                    title: "Ссылка недействительна  | Пифагор",
                },
            },
        ],
    },
];
