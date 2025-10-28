export function getCssVar(name: string): string {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(name)
        .trim();
}

export function formatTimestamp(time: string): string {
    return new Date(time).toLocaleString("fi-FI", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}

export function formatScheduleTime(raw: string | number): string {
    const date = new Date();

    if (typeof raw === "string") {           // "HH:mm" or "HH:mm:ss"
        const [h = 0, m = 0, s = 0] = raw.split(":").map(Number);
        date.setHours(h, m, s);
    }

    return date.toLocaleTimeString("fi-FI");
}
