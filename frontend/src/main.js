import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

import "./styles/main.css";

const app = createApp(App);
const pinia = createPinia();

app.config.errorHandler = (error, instance, info) => {
    console.error("[Ошибка интерфейса платформы]", {
        error,
        instance,
        info,
    });
};

app.use(pinia);
app.use(router);

app.mount("#app");