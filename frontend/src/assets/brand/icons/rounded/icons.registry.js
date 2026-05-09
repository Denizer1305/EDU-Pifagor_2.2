import { getIconCandidates, normalizeIconName } from "./icons.aliases";

const ICON_FILE_PREFIX = "fi-br-";

const iconModules = import.meta.glob("./*.svg", {
    query: "?raw",
    import: "default",
});

const iconLoaders = {};
const iconCache = new Map();
const warnedIcons = new Set();

function stripIconPrefix(fileName) {
    if (fileName.startsWith(ICON_FILE_PREFIX)) {
        return fileName.slice(ICON_FILE_PREFIX.length);
    }

    return fileName;
}

function registerIconLoader(name, loader) {
    if (!name || iconLoaders[name]) {
        return;
    }

    iconLoaders[name] = loader;
}

Object.entries(iconModules).forEach(([path, loader]) => {
    const fileName = path.replace("./", "").replace(".svg", "");
    const shortName = stripIconPrefix(fileName);

    registerIconLoader(fileName, loader);
    registerIconLoader(shortName, loader);
});

export const availableIconNames = Object.freeze(
    Object.keys(iconLoaders).sort(),
);

export function resolveIconName(name) {
    const candidates = getIconCandidates(name);

    return candidates.find((candidate) => {
        return Boolean(iconLoaders[candidate]);
    }) || "";
}

export function hasIcon(name) {
    return Boolean(resolveIconName(name));
}

export async function loadIconSvg(name) {
    const resolvedName = resolveIconName(name);

    if (!resolvedName) {
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

    if (iconCache.has(resolvedName)) {
        return iconCache.get(resolvedName);
    }

    const svgPromise = iconLoaders[resolvedName]();

    iconCache.set(resolvedName, svgPromise);

    return svgPromise;
}
