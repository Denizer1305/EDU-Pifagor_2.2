export const publicNavigationItems = [
    {
        label: "Главная страница",
        description: "Стартовая страница платформы",
        icon: "fas fa-home",
        to: "/",
        match: ["public.home"],
    },
    {
        label: "О платформе",
        description: "Узнайте больше о Пифагоре",
        icon: "fas fa-info-circle",
        to: "/about",
        match: ["public.about"],
    },
    {
        label: "Преподаватели",
        description: "Команда профессионалов",
        icon: "fas fa-chalkboard-user",
        to: "/teachers",
        match: ["public.teachers"],
    },
    {
        label: "Контакты",
        description: "Свяжитесь с нами",
        icon: "fas fa-envelope",
        to: "/contacts",
        match: ["public.contacts"],
    },
];