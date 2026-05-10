export const loginIntroContent = {
    logo: {
        src: "/logo/light/hero-logo.svg",
        alt: "Пифагор — Образовательная платформа",
    },
    badges: [
        {
            icon: "lock",
            text: "Защищённый вход",
        },
        {
            icon: "check-circle",
            text: "Быстрый доступ",
        },
    ],
    title: "С возвращением в Пифагор",
    subtitle:
        "Войдите в личный кабинет, чтобы продолжить обучение, работу с курсами, заданиями, журналом и всей цифровой образовательной средой.",
    meta: [
        {
            icon: "book-open",
            text: "Учёба и курсы",
        },
        {
            icon: "chart-line",
            text: "Прогресс и аналитика",
        },
        {
            icon: "layers",
            text: "Единая среда",
        },
    ],
};

export const loginFormContent = {
    topline: {
        icon: "login",
        text: "Авторизация",
    },
    title: "Вход в аккаунт",
    description:
        "Укажите почту и пароль, чтобы открыть личный кабинет платформы.",
    roles: [
        {
            icon: "student",
            text: "Студенты",
        },
        {
            icon: "teacher",
            text: "Преподаватели",
        },
        {
            icon: "users",
            text: "Родители",
        },
    ],
    fields: {
        email: {
            label: "Электронная почта",
            placeholder: "example@edu-pifagor.ru",
        },
        password: {
            label: "Пароль",
            placeholder: "Введите пароль",
        },
        remember: {
            label: "Запомнить меня на этом устройстве",
        },
    },
    submitLabel: "Войти",
    forgotPassword: {
        label: "Забыли пароль?",
        to: "/auth/forgot-password",
    },
    register: {
        textBefore: "Ещё нет аккаунта?",
        label: "Создать его",
        to: "/auth/register",
        textAfter: "и начать работу с платформой.",
    },
    legal:
        "Авторизация даёт доступ к материалам, заданиям, расписанию, аналитике и другим возможностям платформы.",
};

export const registerIntroContent = {
    logo: {
        src: "/logo/light/hero-logo.svg",
        alt: "Пифагор — Образовательная платформа",
    },
    badges: [
        {
            icon: "shield",
            text: "Безопасный вход",
        },
        {
            icon: "user-add",
            text: "Быстрая регистрация",
        },
    ],
    title: "Присоединяйтесь к Пифагору",
    subtitle:
        "Создайте аккаунт и получите доступ к современной цифровой образовательной среде — спокойно, быстро и без лишних шагов.",
    meta: [
        {
            icon: "student",
            text: "Для студентов",
        },
        {
            icon: "teacher",
            text: "Для преподавателей",
        },
        {
            icon: "users",
            text: "Для родителей",
        },
    ],
};

export const registerFormContent = {
    topline: {
        icon: "user-check",
        text: "Новая учетная запись",
    },
    title: "Регистрация",
    description:
        "Заполните форму ниже, чтобы создать аккаунт и начать работу с платформой.",
    roles: [
        {
            value: "student",
            label: "Студент",
        },
        {
            value: "teacher",
            label: "Преподаватель",
        },
        {
            value: "parent",
            label: "Родитель",
        },
    ],
    fields: {
        role: {
            label: "Выберите роль",
        },
        lastName: {
            label: "Фамилия",
            placeholder: "Иванов",
        },
        firstName: {
            label: "Имя",
            placeholder: "Иван",
        },
        middleName: {
            label: "Отчество",
            placeholder: "Иванович",
        },
        phone: {
            label: "Телефон",
            placeholder: "+7 (999) 123-45-67",
        },
        email: {
            label: "Электронная почта",
            placeholder: "example@edu-pifagor.ru",
        },
        password: {
            label: "Пароль",
            placeholder: "Не менее 8 символов",
        },
        passwordConfirm: {
            label: "Подтверждение пароля",
            placeholder: "Повторите пароль",
        },
        agreement: {
            textBefore: "Я принимаю",
            rulesLabel: "пользовательское соглашение",
            textMiddle: "и соглашаюсь на",
            personalDataLabel: "обработку персональных данных",
        },
    },
    submitLabel: "Создать аккаунт",
    login: {
        textBefore: "Уже есть аккаунт?",
        label: "Войти",
        to: "/auth/login",
    },
    legal:
        "После отправки формы данные можно использовать для подтверждения регистрации и доступа в личный кабинет платформы.",
};

export const emailVerifyIntroContent = {
    logo: {
        src: "/logo/light/hero-logo.svg",
        alt: "Пифагор — Образовательная платформа",
    },
    badges: [
        {
            icon: "envelope-circle-check",
            text: "Подтверждение почты",
        },
        {
            icon: "shield",
            text: "Защита аккаунта",
        },
    ],
    title: "Подтвердите электронную почту",
    subtitle:
        "Мы отправили код подтверждения на вашу почту. Остался один шаг, чтобы завершить регистрацию и активировать аккаунт.",
    meta: [
        {
            icon: "check-circle",
            text: "Регистрация почти завершена",
        },
        {
            icon: "key",
            text: "Безопасная активация",
        },
        {
            icon: "user-lock",
            text: "Защита профиля",
        },
    ],
};

export const emailVerifyFormContent = {
    topline: {
        icon: "envelope-open-text",
        text: "Проверка почты",
    },
    title: "Введите код из письма",
    description:
        "Введите 6-значный код, который был отправлен на вашу электронную почту.",
    meta: [
        {
            icon: "clock",
            text: "Код действует ограниченное время",
        },
        {
            icon: "paper-plane",
            text: "Письмо отправлено автоматически",
        },
    ],
    fields: {
        code: {
            label: "Код подтверждения",
            noteTitle: "Пример:",
            noteText: "если в письме указан код",
            example: "123456",
            noteEnd: "введите его по одной цифре в каждое поле.",
        },
    },
    submitLabel: "Подтвердить почту",
    backLink: {
        label: "Вернуться к регистрации",
        to: "/auth/register",
    },
    resend: {
        text: "Не пришло письмо?",
        label: "Отправить код повторно",
    },
    legal:
        "После подтверждения почты аккаунт будет активирован, и вы сможете войти в систему.",
};

export const teacherOrganizationIntroContent = {
    logo: {
        src: "/logo/light/hero-logo.svg",
        alt: "Пифагор — Образовательная платформа",
    },
    badges: [
        {
            icon: "school",
            text: "Код организации",
        },
        {
            icon: "shield-check",
            text: "Проверка преподавателя",
        },
    ],
    title: "Подключение к образовательной организации",
    subtitle:
        "Введите код, который выдала ваша образовательная организация. После проверки будет создана заявка на привязку преподавателя к организации.",
    meta: [
        {
            icon: "key",
            text: "Проверка кода",
        },
        {
            icon: "user-time",
            text: "Статус заявки",
        },
        {
            icon: "user-check",
            text: "Подтверждение администратором",
        },
    ],
};

export const teacherOrganizationFormContent = {
    topline: {
        icon: "school",
        text: "Привязка преподавателя",
    },
    title: "Введите код организации",
    description:
        "Код нужен, чтобы потвердить вашу связь с образовательной организацией",
    fields: {
        code: {
            label: "Код образовательной организации",
            placeholder: "VLGK-2026",
            previewLabel: "Будет отправлен код:",
            previewEmpty: "код пока не введён",
        },
    },
    statuses: {
        idle: {
            variant: "neutral",
            icon: "info",
            title: "Введите код организации",
            text: "После ввода кода система подготовит заявку на проверку принадлежности к организации.",
        },
        invalid: {
            variant: "warning",
            icon: "exclamation",
            title: "Код слишком короткий",
            text: "Проверьте код. Обычно он содержит не менее 6 символов.",
        },
        pending: {
            variant: "success",
            icon: "user-time",
            title: "Фундамент заявки подготовлен",
            text: "На следующем этапе здесь будет отправка кода на backend и создание заявки в статусе pending.",
        },
    },
    submitLabel: "Подтвердить код",
    backLink: {
        label: "Вернуться ко входу",
        to: "/auth/login",
    },
    help: {
        text: "Нет кода?",
        label: "Обратитесь к администратору образовательной организации.",
        href: "#",
    },
    legal:
        "Код используется только для проверки принадлежности преподавателя к образовательной организации и защиты платформы от несанкционированных подключений.",
};

export const resetPasswordIntroContent = {
    logo: {
        src: "/logo/light/hero-logo.svg",
        alt: "Пифагор — Образовательная платформа",
    },
    badges: [
        {
            icon: "lock",
            text: "Новый пароль",
        },
        {
            icon: "shield",
            text: "Защита аккаунта",
        },
    ],
    title: "Создайте новый пароль",
    subtitle:
        "Придумайте новый пароль для входа в аккаунт. Он должен быть надёжным и отличаться от простых комбинаций.",
    meta: [
        {
            icon: "key",
            text: "Надёжный доступ",
        },
        {
            icon: "shield-check",
            text: "Безопасность аккаунта",
        },
        {
            icon: "check",
            text: "Быстрое восстановление",
        },
    ],
};

export const resetPasswordFormContent = {
    topline: {
        icon: "refresh",
        text: "Сброс пароля",
    },
    title: "Введите новый пароль",
    description:
        "Укажите новый пароль и повторите его ещё раз для подтверждения.",
    fields: {
        password: {
            label: "Новый пароль",
            placeholder: "Введите новый пароль",
        },
        passwordConfirm: {
            label: "Повторите пароль",
            placeholder: "Повторите новый пароль",
        },
    },
    strength: {
        label: "Надёжность пароля",
    },
    match: {
        success: "Пароли совпадают.",
        error: "Пароли пока не совпадают.",
    },
    note: {
        title: "Подсказка:",
        text: "используйте пароль, который легко запомнить вам, но сложно подобрать постороннему.",
    },
    submitLabel: "Сохранить новый пароль",
    backLink: {
        label: "Вернуться ко входу",
        to: "/auth/login",
    },
    legal:
        "После сохранения нового пароля старый пароль больше не будет действовать.",
};

export const forgotPasswordIntroContent = {
    logo: {
        src: "/logo/light/hero-logo.svg",
        alt: "Пифагор — Образовательная платформа",
    },
    badges: [
        {
            icon: "key",
            text: "Восстановление доступа",
        },
        {
            icon: "shield",
            text: "Безопасный вход",
        },
    ],
    title: "Забыли пароль?",
    subtitle:
        "Ничего страшного. Укажите электронную почту, привязанную к аккаунту, и мы отправим инструкции для восстановления доступа.",
    meta: [
        {
            icon: "envelope",
            text: "Ссылка придёт на почту",
        },
        {
            icon: "lock",
            text: "Безопасная процедура",
        },
        {
            icon: "clock",
            text: "Несколько минут",
        },
    ],
};

export const forgotPasswordFormContent = {
    topline: {
        icon: "envelope-open-text",
        text: "Восстановление пароля",
    },
    title: "Введите вашу почту",
    description:
        "Мы отправим письмо со ссылкой или кодом для сброса пароля.",
    fields: {
        email: {
            label: "Электронная почта",
            placeholder: "Введите вашу почту",
        },
    },
    statuses: {
        invalid: "Введите корректный адрес электронной почты.",
        sent: "Если такой аккаунт существует, письмо для восстановления будет отправлено на указанную почту.",
    },
    note: {
        title: "Важно:",
        text: "укажите именно тот адрес электронной почты, который использовался при регистрации аккаунта.",
    },
    submitLabel: "Отправить письмо",
    backLink: {
        label: "Вернуться ко входу",
        to: "/auth/login",
    },
    support: {
        text: "Не получается восстановить доступ?",
        label: "Свяжитесь с нами",
        to: "/contacts",
    },
    legal:
        "Продолжая, вы подтверждаете, что используете собственный адрес электронной почты для восстановления доступа.",
};

export const logoutPageContent = {
    logo: {
        src: "/logo/light/logo.svg",
        alt: "Пифагор",
        to: "/",
        ariaLabel: "Пифагор — на главную",
    },
    title: "Завершить сеанс?",
    text:
        "Вы собираетесь выйти из личного кабинета. После выхода для продолжения работы потребуется повторный вход в систему.",
    info: [
        {
            icon: "shield",
            title: "Безопасное завершение",
            text: "Сеанс будет завершён на текущем устройстве.",
        },
        {
            icon: "login",
            title: "Повторный вход",
            text: "Вы сможете войти снова в любое время через страницу авторизации.",
        },
    ],
    cancelAction: {
        label: "Вернуться назад",
        icon: "arrow-left",
        to: "/auth/login",
    },
    confirmAction: {
        label: "Выйти из аккаунта",
        icon: "check",
        to: "/",
    },
};

export const checkEmailPageContent = {
    icon: "envelope-open",
    badge: {
        icon: "paper-plane",
        text: "Письмо отправлено",
    },
    title: "Проверьте электронную почту",
    text:
        "Мы отправили письмо с дальнейшими инструкциями. Откройте почтовый ящик и перейдите по ссылке из письма, чтобы продолжить.",
    items: [
        {
            icon: "envelope",
            title: "Проверьте входящие",
            text: "Письмо должно прийти на адрес, указанный при регистрации или восстановлении доступа.",
        },
        {
            icon: "search",
            title: "Посмотрите папку «Спам»",
            text: "Иногда автоматические письма могут попадать в нежелательную почту.",
        },
        {
            icon: "clock",
            title: "Ссылка действует ограниченное время",
            text: "Если ссылка устареет, можно будет запросить новое письмо.",
        },
    ],
    actions: [
        {
            label: "Вернуться ко входу",
            icon: "login",
            to: "/auth/login",
            variant: "primary",
        },
        {
            label: "Запросить письмо заново",
            icon: "refresh",
            to: "/auth/forgot-password",
            variant: "light",
        },
    ],
    note:
        "После подключения backend эта страница будет использоваться после регистрации и восстановления пароля.",
};

export const emailVerifiedPageContent = {
    icon: "check-circle",
    badge: {
        icon: "shield-check",
        text: "Почта подтверждена",
    },
    title: "Электронная почта подтверждена",
    text:
        "Ваш адрес успешно подтверждён. Теперь аккаунт готов к дальнейшей настройке и входу в личный кабинет.",
    items: [
        {
            icon: "check",
            title: "Аккаунт активирован",
            text: "Подтверждение почты завершает базовую проверку пользователя.",
        },
        {
            icon: "login",
            title: "Можно войти в систему",
            text: "Используйте почту и пароль, указанные при регистрации.",
        },
        {
            icon: "school",
            title: "Для преподавателей",
            text: "Если вы преподаватель, следующим шагом можно привязаться к образовательной организации.",
        },
    ],
    actions: [
        {
            label: "Войти в аккаунт",
            icon: "login",
            to: "/auth/login",
            variant: "primary",
        },
        {
            label: "Ввести код организации",
            icon: "school",
            to: "/auth/teacher-organization",
            variant: "light",
        },
    ],
    note:
        "После подключения API переход на эту страницу будет выполняться после успешной проверки email-токена.",
};

export const teacherPendingPageContent = {
    icon: "user-time",
    badge: {
        icon: "school",
        text: "Заявка отправлена",
    },
    title: "Заявка преподавателя ожидает подтверждения",
    text:
        "Код организации принят. Связь преподавателя с образовательной организацией создана в статусе ожидания.",
    items: [
        {
            icon: "user-time",
            title: "Статус pending",
            text: "Пока заявка ожидает решения администратора организации.",
        },
        {
            icon: "shield-check",
            title: "Администратор проверит заявку",
            text: "После проверки преподаватель будет переведён в статус active.",
        },
        {
            icon: "bell",
            title: "Уведомление о результате",
            text: "Позже здесь можно будет подключить уведомление о подтверждении или отклонении заявки.",
        },
    ],
    actions: [
        {
            label: "Вернуться ко входу",
            icon: "login",
            to: "/auth/login",
            variant: "primary",
        },
        {
            label: "Связаться с поддержкой",
            icon: "envelope",
            to: "/contacts",
            variant: "light",
        },
    ],
    note:
        "Эта страница нужна для сценария teacher ↔ organization со статусами pending / active / rejected.",
};

export const linkExpiredPageContent = {
    icon: "exclamation",
    badge: {
        icon: "clock",
        text: "Ссылка недействительна",
    },
    title: "Ссылка устарела или уже использована",
    text:
        "Ссылка подтверждения могла истечь, быть использована ранее или стать недействительной после повторного запроса.",
    items: [
        {
            icon: "clock",
            title: "Время действия истекло",
            text: "Защитные ссылки обычно работают ограниченное время.",
        },
        {
            icon: "shield",
            title: "Это безопасно",
            text: "Мы не активируем действия по устаревшим или недействительным ссылкам.",
        },
        {
            icon: "refresh",
            title: "Можно запросить новую ссылку",
            text: "Выберите нужный сценарий и отправьте письмо повторно.",
        },
    ],
    actions: [
        {
            label: "Восстановить пароль",
            icon: "key",
            to: "/auth/forgot-password",
            variant: "primary",
        },
        {
            label: "Вернуться ко входу",
            icon: "login",
            to: "/auth/login",
            variant: "light",
        },
    ],
    note:
        "Эта страница будет использоваться для просроченных ссылок подтверждения email, восстановления пароля и приглашений.",
};
