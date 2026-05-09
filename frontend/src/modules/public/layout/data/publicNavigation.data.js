export const publicNavigationItems = [
    {
        label: "Главная страница",
        description: "Стартовая страница платформы",
        icon: "home",
        to: "/",
        match: ["public.home"],
    },
    {
        label: "О платформе",
        description: "Узнайте больше о Пифагоре",
        icon: "info",
        to: "/about",
        match: ["public.about"],
    },
    {
        label: "Преподаватели",
        description: "Команда профессионалов",
        icon: "teacher",
        to: "/teachers",
        match: ["public.teachers"],
    },
    {
        label: "Контакты",
        description: "Свяжитесь с нами",
        icon: "envelope",
        to: "/contacts",
        match: ["public.contacts"],
    },
];
