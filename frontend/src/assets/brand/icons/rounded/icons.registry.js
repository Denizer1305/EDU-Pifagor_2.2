import { getIconCandidates, normalizeIconName } from "./icons.aliases";

const ICON_FILE_PREFIX = "fi-br-";

const iconModules = import.meta.glob("./*.svg", {
    eager: true,
    query: "?raw",
    import: "default",
});

function stripIconPrefix(fileName) {
    if (fileName.startsWith(ICON_FILE_PREFIX)) {
        return fileName.slice(ICON_FILE_PREFIX.length);
    }

    return fileName;
}

function registerIcon(registry, name, svg) {
    if (!name || registry[name]) {
        return;
    }

    registry[name] = svg;
}

const iconRegistry = Object.entries(iconModules).reduce((registry, [path, svg]) => {
    const fileName = path.replace("./", "").replace(".svg", "");
    const shortName = stripIconPrefix(fileName);

    registerIcon(registry, fileName, svg);
    registerIcon(registry, shortName, svg);

    return registry;
}, {});

export const availableIconNames = Object.freeze(
    Object.keys(iconRegistry).sort(),
);

const warnedIcons = new Set();

export function resolveIconName(name) {
    const candidates = getIconCandidates(name);

    return candidates.find((candidate) => {
        return Boolean(iconRegistry[candidate]);
    }) || "";
}

export function hasIcon(name) {
    return Boolean(resolveIconName(name));
}

export function getIconSvg(name) {
    const resolvedName = resolveIconName(name);

    if (resolvedName) {
        return iconRegistry[resolvedName];
    }

    if (import.meta.env.DEV) {
        const normalizedName = normalizeIconName(name);

        if (normalizedName && !warnedIcons.has(normalizedName)) {
            warnedIcons.add(normalizedName);

            console.warn(
                `[BaseIcon] Иконка "${name}" не найдена в src/assets/brand/icons/rounded/. ` +
                "Проверь имя файла или добавь алиас в icons.aliases.js.",
            );
        }
    }

    return "";
}
