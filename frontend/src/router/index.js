import { createRouter, createWebHistory } from "vue-router";

import { adminRoutes } from "./routes.admin";
import { authRoutes } from "./routes.auth";
import { errorRoutes } from "./routes.errors";
import { parentRoutes } from "./routes.parent";
import { publicRoutes } from "./routes.public";
import { studentRoutes } from "./routes.student";
import { teacherRoutes } from "./routes.teacher";
import { setupRouterGuards } from "./guards";

const routes = [
    ...publicRoutes,
    ...authRoutes,
    ...adminRoutes,
    ...teacherRoutes,
    ...studentRoutes,
    ...parentRoutes,
    ...errorRoutes,
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
    scrollBehavior() {
        return {
            top: 0,
            behavior: "smooth",
        };
    },
});

setupRouterGuards(router);

export default router;
