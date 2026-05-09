const createCandidates = (...names) => names.filter(Boolean);

export const ICON_ALIASES = {
    /*
     * Navigation / layout
     */
    home: createCandidates("home"),
    "fa-home": createCandidates("home"),

    about: createCandidates("info", "interrogation"),
    info: createCandidates("info", "interrogation"),
    "info-circle": createCandidates("info"),
    "circle-info": createCandidates("info", "comment-info"),
    "fa-info-circle": createCandidates("info"),
    "fa-circle-info": createCandidates("info", "comment-info"),

    contacts: createCandidates("address-book", "envelope", "mail"),
    contact: createCandidates("address-book", "envelope", "mail"),
    "address-book": createCandidates("address-book"),
    "fa-address-book": createCandidates("address-book"),

    teachers: createCandidates("presentation", "school", "e-learning", "user"),
    teacher: createCandidates("presentation", "school", "e-learning", "user"),
    "chalkboard-user": createCandidates("presentation", "school", "e-learning", "user"),
    "fa-chalkboard-user": createCandidates("presentation", "school", "e-learning", "user"),

    student: createCandidates("graduation-cap", "child-head", "user"),
    "user-graduate": createCandidates("graduation-cap", "child-head", "user"),
    "fa-user-graduate": createCandidates("graduation-cap", "child-head", "user"),

    profile: createCandidates("user", "id-badge"),
    user: createCandidates("user"),
    users: createCandidates("user", "user-add"),
    "fa-users": createCandidates("user", "user-add"),

    login: createCandidates("sign-in-alt", "sign-in"),
    "sign-in-alt": createCandidates("sign-in-alt", "sign-in"),
    "fa-sign-in-alt": createCandidates("sign-in-alt", "sign-in"),

    logout: createCandidates("sign-out-alt", "sign-out"),
    "sign-out-alt": createCandidates("sign-out-alt", "sign-out"),

    menu: createCandidates("menu-burger"),
    burger: createCandidates("menu-burger"),
    bars: createCandidates("menu-burger"),

    close: createCandidates("cross-small", "cross", "cross-circle"),
    times: createCandidates("cross-small", "cross", "cross-circle"),
    "fa-times": createCandidates("cross-small", "cross", "cross-circle"),

    sun: createCandidates("sun"),
    "fa-sun": createCandidates("sun"),

    moon: createCandidates("moon"),
    "fa-moon": createCandidates("moon"),

    /*
     * Arrows
     */
    "arrow-right": createCandidates("arrow-right", "arrow-small-right", "angle-right"),
    "fa-arrow-right": createCandidates("arrow-right", "arrow-small-right", "angle-right"),

    "arrow-left": createCandidates("arrow-left", "arrow-small-left", "angle-left"),
    "arrow-up": createCandidates("arrow-up", "arrow-small-up", "angle-up"),
    "arrow-down": createCandidates("arrow-down", "arrow-small-down", "angle-down"),

    "chevron-right": createCandidates("angle-small-right", "angle-right"),
    "chevron-left": createCandidates("angle-small-left", "angle-left"),
    "chevron-up": createCandidates("angle-small-up", "angle-up"),
    "chevron-down": createCandidates("angle-small-down", "angle-down"),

    "angle-right": createCandidates("angle-right", "angle-small-right"),
    "angle-left": createCandidates("angle-left", "angle-small-left"),
    "angle-up": createCandidates("angle-up", "angle-small-up"),
    "angle-down": createCandidates("angle-down", "angle-small-down"),

    /*
     * Common actions
     */
    add: createCandidates("add", "plus", "plus-small"),
    plus: createCandidates("plus", "plus-small", "add"),
    minus: createCandidates("minus", "minus-small"),

    check: createCandidates("check", "checkbox"),
    "check-circle": createCandidates("checkbox", "check"),
    "fa-check-circle": createCandidates("checkbox", "check"),

    checkbox: createCandidates("checkbox", "check"),

    edit: createCandidates("edit", "edit-alt", "pencil"),
    pencil: createCandidates("pencil", "edit"),
    delete: createCandidates("trash", "delete"),
    trash: createCandidates("trash", "delete"),

    download: createCandidates("download", "cloud-download"),
    upload: createCandidates("upload", "cloud-upload"),
    search: createCandidates("search", "search-alt"),
    filter: createCandidates("filter"),
    sort: createCandidates("apps-sort", "settings-sliders"),
    copy: createCandidates("copy", "copy-alt", "duplicate"),

    refresh: createCandidates("refresh", "redo", "redo-alt"),
    spinner: createCandidates("spinner", "spinner-alt", "refresh"),
    "fa-spinner": createCandidates("spinner", "spinner-alt", "refresh"),

    warning: createCandidates("exclamation", "shield-exclamation", "ban"),
    exclamation: createCandidates("exclamation"),

    /*
     * Brand / social
     */
    vk: createCandidates("vk"),
    "fa-vk": createCandidates("vk"),

    max: createCandidates("max"),

    telegram: createCandidates("paper-plane"),
    "fa-telegram": createCandidates("paper-plane"),

    youtube: createCandidates("youtube"),
    yandex: createCandidates("yandex"),

    /*
     * Public home
     */
    flag: createCandidates("flag"),
    "fa-flag": createCandidates("flag"),

    shield: createCandidates("shield", "shield-check"),
    "shield-alt": createCandidates("shield", "shield-check"),
    "fa-shield-alt": createCandidates("shield", "shield-check"),

    "shield-heart": createCandidates("shield-check", "shield", "heart"),
    "fa-shield-heart": createCandidates("shield-check", "shield", "heart"),

    "grid-2": createCandidates("grid", "grid-alt", "apps"),
    grid: createCandidates("grid", "grid-alt", "apps"),
    apps: createCandidates("apps", "grid"),

    "book-open": createCandidates("book-alt", "book"),
    book: createCandidates("book", "book-alt"),
    "book-alt": createCandidates("book-alt", "book"),

    "folder-tree": createCandidates("folder", "folder-add"),
    folder: createCandidates("folder", "folder-add"),

    "file-lines": createCandidates("document-signed", "document", "file", "text"),
    document: createCandidates("document", "document-signed", "file"),
    file: createCandidates("file", "document"),

    video: createCandidates("video-camera", "film", "play"),
    "fa-video": createCandidates("video-camera", "film", "play"),

    "pen-ruler": createCandidates("pencil", "protractor", "edit"),
    "chart-line": createCandidates("chart-connected", "chart-histogram", "stats"),
    analytics: createCandidates("stats", "chart-connected", "chart-histogram"),
    stats: createCandidates("stats", "chart-histogram"),

    "chart-pie": createCandidates("chart-pie", "chart-pie-alt"),
    "fa-chart-pie": createCandidates("chart-pie", "chart-pie-alt"),

    "list-check": createCandidates("list-check", "list", "checkbox"),
    list: createCandidates("list"),
    "calendar-days": createCandidates("calendar"),
    calendar: createCandidates("calendar"),

    comments: createCandidates("comments", "comment", "comment-alt"),
    "fa-comments": createCandidates("comments", "comment", "comment-alt"),

    sparkles: createCandidates("magic-wand", "star", "star-octogram", "confetti"),
    "fa-sparkles": createCandidates("magic-wand", "star", "star-octogram", "confetti"),

    "check-double": createCandidates("checkbox", "check"),

    /*
     * About page
     */
    scroll: createCandidates("document-signed", "document", "diploma"),
    "fa-scroll": createCandidates("document-signed", "document", "diploma"),

    "building-columns": createCandidates("bank", "building", "school"),
    "fa-building-columns": createCandidates("bank", "building", "school"),

    building: createCandidates("building", "bank", "school"),
    "fa-building": createCandidates("building", "bank", "school"),

    school: createCandidates("school", "bank", "building"),
    organization: createCandidates("school", "bank", "building"),

    link: createCandidates("link"),
    "fa-link": createCandidates("link"),

    "feather-pointed": createCandidates("pencil", "edit-alt", "marker"),
    "fa-feather-pointed": createCandidates("pencil", "edit-alt", "marker"),

    brain: createCandidates("head-side-thinking", "chart-network", "network"),
    "ai-brain": createCandidates("head-side-thinking", "chart-network", "network"),
    "neural-network": createCandidates("chart-network", "network"),
    "fa-brain": createCandidates("head-side-thinking", "chart-network", "network"),

    heart: createCandidates("heart"),
    "fa-heart": createCandidates("heart"),

    database: createCandidates("database"),
    "fa-database": createCandidates("database"),

    language: createCandidates("letter-case", "text", "world", "globe"),
    translate: createCandidates("letter-case", "text", "world", "globe"),
    "fa-language": createCandidates("letter-case", "text", "world", "globe"),

    "user-tie": createCandidates("id-badge", "user", "briefcase"),
    "fa-user-tie": createCandidates("id-badge", "user", "briefcase"),

    trophy: createCandidates("trophy"),
    diploma: createCandidates("diploma"),

    /*
     * Teachers page
     */
    medal: createCandidates("trophy", "diploma", "badge"),
    "fa-medal": createCandidates("trophy", "diploma", "badge"),

    award: createCandidates("trophy", "diploma", "badge"),
    "fa-award": createCandidates("trophy", "diploma", "badge"),

    certificate: createCandidates("diploma", "badge", "document-signed"),

    /*
     * Contacts page
     */
    "location-dot": createCandidates("map-marker", "location-alt", "home-location"),
    "fa-location-dot": createCandidates("map-marker", "location-alt", "home-location"),

    "map-pin": createCandidates("map-marker", "location-alt"),
    location: createCandidates("map-marker", "location-alt"),

    envelope: createCandidates("envelope", "mail"),
    mail: createCandidates("mail", "envelope"),
    "fa-envelope": createCandidates("envelope", "mail"),

    phone: createCandidates("phone-call"),
    "fa-phone": createCandidates("phone-call"),

    "phone-volume": createCandidates("phone-call"),
    "fa-phone-volume": createCandidates("phone-call"),

    clock: createCandidates("clock", "alarm-clock"),
    "fa-clock": createCandidates("clock", "alarm-clock"),

    hashtag: createCandidates("hastag"),
    hastag: createCandidates("hastag"),
    "fa-hashtag": createCandidates("hastag"),

    map: createCandidates("map"),
    "fa-map": createCandidates("map"),

    route: createCandidates("road", "navigation", "map"),
    "fa-route": createCandidates("road", "navigation", "map"),

    "map-location-dot": createCandidates("map-marker", "map-marker-home", "home-location", "map"),
    "fa-map-location-dot": createCandidates("map-marker", "map-marker-home", "home-location", "map"),

    "paper-plane": createCandidates("paper-plane"),
    "fa-paper-plane": createCandidates("paper-plane"),

    /*
     * Learning / education
     */
    course: createCandidates("e-learning", "book-alt", "book"),
    courses: createCandidates("e-learning", "book-alt", "book"),
    lesson: createCandidates("presentation", "book-alt"),
    assignment: createCandidates("list-check", "document-signed", "form"),
    test: createCandidates("test", "text-check"),
    journal: createCandidates("notebook", "book-alt"),
    schedule: createCandidates("calendar", "clock"),
    grade: createCandidates("badge", "trophy"),
    attendance: createCandidates("checkbox", "user-time"),
    subject: createCandidates("book", "book-alt"),
    materials: createCandidates("folder", "resources"),
    resources: createCandidates("resources", "folder"),

    /*
     * Status / small utility
     */
    circle: createCandidates("circle-small", "circle"),
    "fa-circle": createCandidates("circle-small", "circle"),

    lock: createCandidates("lock", "lock-alt"),
    unlock: createCandidates("unlock"),

    eye: createCandidates("eye"),
    "eye-crossed": createCandidates("eye-crossed"),

    star: createCandidates("star", "star-octogram"),

    handshake: createCandidates("link", "briefcase", "users"),
    "fa-handshake": createCandidates("link", "briefcase", "users"),

    lightbulb: createCandidates("bulb"),
    "fa-lightbulb": createCandidates("bulb"),
};

export function normalizeIconName(value) {
    if (!value) {
        return "";
    }

    const rawValue = String(value).trim();

    if (!rawValue) {
        return "";
    }

    const classParts = rawValue.split(/\s+/);
    const fontAwesomeClass = classParts.find((part) => {
        return part.startsWith("fa-")
            && !["fa-solid", "fa-regular", "fa-brands", "fas", "far", "fab", "fa"].includes(part);
    });

    const preparedValue = fontAwesomeClass || rawValue;

    return preparedValue
        .replace(/^fas\s+/, "")
        .replace(/^far\s+/, "")
        .replace(/^fab\s+/, "")
        .replace(/^fa\s+/, "")
        .replace(/^fa-/, "")
        .replace(/^fi-br-/, "")
        .replace(/^icon-/, "")
        .replace(/_/g, "-")
        .replace(/\s+/g, "-")
        .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
        .toLowerCase();
}

export function getIconCandidates(value) {
    const normalizedName = normalizeIconName(value);

    if (!normalizedName) {
        return [];
    }

    const aliases = ICON_ALIASES[normalizedName] || ICON_ALIASES[`fa-${normalizedName}`] || [];

    return [
        normalizedName,
        `fi-br-${normalizedName}`,
        ...aliases,
        ...aliases.map((alias) => `fi-br-${alias}`),
    ].filter((name, index, array) => {
        return name && array.indexOf(name) === index;
    });
}
