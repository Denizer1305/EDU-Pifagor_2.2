export const authRoutes = [
    {
        path: "/auth/login",
        name: "auth.login",
        component: () => import("../pages/auth/LoginPage.vue"),
        meta: {
            isPublic: true,
            guestOnly: true,
            title: "Вход — Пифагор",
        },
    },
    {
        path: "/auth/register",
        name: "auth.register",
        component: () => import("../pages/auth/RegisterPage.vue"),
        meta: {
            isPublic: true,
            guestOnly: true,
            title: "Регистрация — Пифагор",
        },
    },
    {
        path: "/auth/password-reset",
        name: "auth.password-reset",
        component: () => import("../pages/auth/PasswordResetPage.vue"),
        meta: {
            isPublic: true,
            guestOnly: true,
            title: "Восстановление пароля — Пифагор",
        },
    },
    {
        path: "/auth/email-verify",
        name: "auth.email-verify",
        component: () => import("../pages/auth/EmailVerifyPage.vue"),
        meta: {
            isPublic: true,
            title: "Подтверждение почты — Пифагор",
        },
    },
];